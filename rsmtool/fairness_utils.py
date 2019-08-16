"""
Utility classes and functions related to computing fairness evaluations

:author: Anastassia Loukina (aloukina@ets.org)
:author: Jeremy Biggs (jbiggs@ets.org)
:author: Nitin Madnani (nmadnani@ets.org)

:date: 07/29/2019
:organization: ETS
"""

import pandas as pd
import pickle 
import numpy as np

from os.path import join

import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

from rsmtool.writer import DataWriter
from rsmtool.container import DataContainer



def convert_to_ordered_category(group_values):
    """
    Convert supplied series to an ordered category
    with levels ordered by category size.
    If multiple categories have the same size,
    the order is determined alphabetically. 

    Parameters
    ----------
    group_values: pandas Series

    Returns
    -------
    group_ordered_category: pandas Series
    """
    
    # get ordered list by size

    # We convert the  value counts to data frame to allow for multilevel sorting.
    # This makes sure that the order is consistent and reproducible across runs
    # when there are more than
    # one group with the maximum number of occurrences. 
    df_groups_by_size = pd.DataFrame(group_values.value_counts()).reset_index()
    df_groups_by_size.columns = ['group_name', 'count']
    df_groups_by_size_sorted = df_groups_by_size.sort_values(['count', 'group_name'],
                                                            ascending=[False, True])
    groups_by_size = df_groups_by_size_sorted['group_name'].values

    #convert to category and reorder
    group_category = group_values.astype("category")
    group_ordered_category = group_category.cat.reorder_categories(groups_by_size,
                                                                   ordered=True)
    return group_ordered_category
    



def get_coefficients(fit, base_category):
    
    """
    Extract estimates, significance, and confidence intervals
    for members of the group of interest. The names of the 
    predictors are processed to remove the prefix added by Statmodels.
    The name of the base category is added in parenthesis to the Intercept. 

    Parameters:
    -----------
    fit: pandas.stats.ols.OLS
        Linear regression object fitted using statsmodels

    base_category: str
        Name of the group used as reference category when fitting the model

    Returns:
    -------
    df_results: pandas DataFrame
        A dataframe with rows for each category and the following columns:
        - estimate
        - P>[t]
        - Lower and upper boundaries for 95% confidence intervals
    """
        
    # extract the data we need
    df_results = pd.concat([fit.params, fit.pvalues, fit.conf_int()], axis=1)
        
    df_results.columns = ['estimate', 'P>[t]', '[0.025', '0.975]']
        
    # identify the rows we are interested in
    groups = ['Intercept'] + [v for v in df_results.index if 'group' in v]
        
    df_results = df_results.loc[groups]
        
    # rename the rows
    df_results.index = [v.split('.')[1].strip(']') 
                            if not v == 'Intercept' 
                            else 'Intercept ({})'.format(base_category)
                            for v in df_results.index]
        
    return df_results




def write_fairness_results(fit_dictionary,
                           fairness_container,
                           group,
                           output_dir,
                           experiment_id, 
                           file_format):
    """
    Save the results of fairness analysis to disk.

    Parameters
    ----------
    fit_dictionary: dict
        A dictionary of fitted models generated by `get_fairness_analyses()`
    fairness_container: container.DataContainer
        A data container with the results of fairness analysis generated by `get_fairness_analyses()`
    group: str
        The subgroup considered in this analysis
    output_dir: str
        The directory where the results will be saved
    experiment_id: str
        Experiment id
    file_format: str
        File format for data files
    """
    
    # let's first save model files and summaries
    for model in fit_dictionary:
        fit = fit_dictionary[model]

        ols_file = join(output_dir, '{}_{}_by_{}.ols'.format(experiment_id,
                                                             model,
                                                             group))
        summary_file = join(output_dir, '{}_{}_by_{}_ols_summary.txt'.format(experiment_id,
                                                                             model,
                                                                             group))
        with open(ols_file, 'wb') as olsf, open(summary_file, 'w') as summf:
            pickle.dump(fit, olsf)
            summf.write(str(fit.summary()))
            
    # Now let's write out the content of the data container
    writer = DataWriter(experiment_id)
    writer.write_experiment_output(output_dir,
                                   fairness_container,
                                   file_format=file_format,
                                   index=True)

    
    
def get_fairness_analyses(df,
                          group,
                          system_score_column,
                          human_score_column='sc1'):
    """ 
    Compute fairness analyses described in Loukina et al. (2019) https://aclweb.org/anthology/papers/W/W19/W19-4401/
    The functions computes how muach variance group memebership explains in 
    overall score accuracy (osa), overall score difference (osd) and conditional score difference (csd). 
    See paper for further detail. 

    Parameters
    ----------
    df: pandas DataFrame
        A dataframe containing columns with numeric human scores, numeric system scores
        and a column showing group membership
    group: str
        Name of the column containing group membership
    system_score_column: str
        Name of the column containing system scores
    human_score_column: str
        Name of the column containing human scores

    Returns
    -------
    model_dict: dictionary
        A dictionary with different proposed metrics as keys
        and fitted models as values
    fairness_container: container.DataContainer
        A datacontainer with the following datasets:
            - `estimates_METRICS_by_GROUP` where `GROUP` corresponds to group
            and `METRICS` can be osa, osd and csd
            Estimates for each group computed by the respective models
            - `fairness_metrics_by_GROUP` - a summary of model fits (R2 and p values)
    """
    
    # compute error and squared error

    df['error'] = df[system_score_column]-df[human_score_column]
    df['SE'] = df['error']**2

    # convert group values to category and reorder them using 
    # the largest category as reference
    
    df['group'] = convert_to_ordered_category(df[group])
    base_group = df['group'].cat.categories[0]
    df['sc1_cat'] = convert_to_ordered_category(df[human_score_column])

    # Overall score accuracy (OSA)
    # Variance in squared error explained by L1
    
    # fit the model
    osa_model = smf.ols(formula='SE ~ group', data=df)
    osa_fit = osa_model.fit()
    
    # collect the results
    osa_dict = {'R2': osa_fit.rsquared_adj,
               'sig': osa_fit.f_pvalue}

    osa_results = pd.Series(osa_dict, name='Overall score accuracy')

    df_coefficients_osa = get_coefficients(osa_fit, base_group)

    # Overall score difference (OSD)
    # variance in signed residuals (raw error) explained by L1

    # fit the model
    osd_model = smf.ols(formula='error ~ group', data=df)
    osd_fit = osd_model.fit()
    
    # collect the results
    osd_dict = {'R2': osd_fit.rsquared_adj,
               'sig': osd_fit.f_pvalue}

    osd_results = pd.Series(osd_dict, name='Overall score difference')

    df_coefficients_osd = get_coefficients(osd_fit, base_group)
    
    # conditional score difference CSD 
    # Variance in score difference conditioned on Native language
    
    # fit "null" model with human score only
    csd_null_mod = smf.ols(formula='error ~ sc1_cat', data=df)
    csd_null_fit = csd_null_mod.fit()

    # fit model with both human score and group 
    csd_mod = smf.ols(formula='error ~ group + sc1_cat', data=df)
    csd_fit = csd_mod.fit()

    # compare the two models using anova_lm
    # we filter warnings for this function because we get 
    # runtime warning due to NaNs in the data.
    # these seem to be by design: https://groups.google.com/forum/#!topic/pystatsmodels/-flY0cNnb3k
    np.warnings.filterwarnings('ignore')
    anova_results = anova_lm(csd_null_fit, csd_fit)
    # we reset warnings
    np.warnings.resetwarnings()
    
    # collect the results. Note that R2 in this case is a difference
    # in R2 between the two models and significance is obtained from anova
    csd_dict = {'R2': csd_fit.rsquared_adj - csd_null_fit.rsquared_adj,
               'sig': anova_results.values[1][-1]}
    csd_results = pd.Series(csd_dict, name='Conditional score difference')

    df_coefficients_csd = get_coefficients(osd_fit, base_group)

    # create a summary table

    df_r2_all = pd.concat([osa_results, osd_results, csd_results], axis=1, sort=True)
    df_r2_all['base_category'] = base_group
    
    # assemble all datasets into a DataContainer

    datasets = [{'name': 'estimates_osa_by_{}'.format(group),
                 'frame': df_coefficients_osa},
                {'name': 'estimates_osd_by_{}'.format(group),
                 'frame': df_coefficients_osd},
                {'name': 'estimates_csd_by_{}'.format(group),
                 'frame': df_coefficients_csd},
                {'name': 'fairness_metrics_by_{}'.format(group),
                 'frame': df_r2_all}]
    
    # assemble all models into a dictionary
    model_dict = {'osa': osa_fit,
                  'osd': osd_fit,
                  'csd': csd_fit}
    
    return model_dict, DataContainer(datasets=datasets)
    
    
    
    