
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from info_plot_utils import _target_plot, _prepare_data_x, _actual_plot, _actual_plot_title


def actual_plot(pdp_isolate_out, feature_name, figsize=None, plot_params=None,
                multi_flag=False, which_class=None, ncols=None):
    """
    Plot actual prediction distribution through feature grids

    :param pdp_isolate_out: instance of pdp_isolate_obj
        a calculated pdp_isolate_obj instance
    :param feature_name: tring
        name of the feature, not necessary the same as the column name
    :param figsize: (width, height), default=None
        figure size
    :param plot_params: dict, default=None
        values of plot parameters
    :param multi_flag: boolean, default=False
        whether it is a subplot of a multiclass plot
    :param which_class: integer, default=None
        which class to plot
    :param ncols: integer, default=None
        used under multi-class mode
    """

    # check which_class
    if multi_flag and which_class >= len(pdp_isolate_out.keys()):
        raise ValueError('which_class: class does not exist')

    if figsize is None:
        figwidth = 16
    else:
        figwidth = figsize[0]

    # draw graph title
    plt.figure(figsize=(figwidth, figwidth / 6.7))
    ax1 = plt.subplot(111)

    if type(pdp_isolate_out) == dict and not multi_flag:
        n_classes = len(pdp_isolate_out.keys())
        _actual_plot_title(feature_name=feature_name, ax=ax1, figsize=figsize,
                                           multi_flag=multi_flag, which_class=which_class, plot_params=plot_params)

        if ncols is None:
            ncols = 2
        nrows = int(np.ceil(float(n_classes) / ncols))

        plt.figure(figsize=(figwidth, (figwidth / ncols) * nrows))
        outer = GridSpec(nrows, ncols, wspace=0.2, hspace=0.2)

        for n_class in range(n_classes):
            _actual_plot(pdp_isolate_out=pdp_isolate_out['class_%d' % n_class],
                                         feature_name=feature_name + ' class_%d' % n_class,
                                         figwidth=figwidth, plot_params=plot_params, outer=outer[n_class])
    else:
        if multi_flag:
            _pdp_isolate_out = pdp_isolate_out['class_%d' % which_class]
        else:
            _pdp_isolate_out = pdp_isolate_out

        _actual_plot_title(feature_name=feature_name, ax=ax1,
                                           figsize=figsize, multi_flag=multi_flag, which_class=which_class, plot_params=plot_params)

        _actual_plot(pdp_isolate_out=_pdp_isolate_out, feature_name=feature_name,
                                     figwidth=figwidth, plot_params=plot_params, outer=None)


def target_plot(df, feature, feature_name, target, num_grid_points=10, grid_type='percentile',
                percentile_range=None, grid_range=None, cust_grid_points=None, show_percentile=False,
                figsize=None, ax=None, plot_params=None):
    """Plot average target value across different feature values (feature grids)

    Parameters:
    -----------

    :param df: pandas DataFrame
        data set to investigate on, should contain at least
        the feature to investigate as well as the target
    :param feature: string or list
        feature or feature list to investigate
        for one-hot encoding features, feature list is required
    :param feature_name: string
        name of the feature, not necessary a column name
    :param target: string or list
        column name or column name list for target value
        for multi-class problem, a list of one-hot encoding target column
    :param num_grid_points: integer, optional, default=10
        number of grid points for numeric feature
    :param grid_type: string, optional, default='percentile'
        'percentile' or 'equal'
        type of grid points for numeric feature
    :param percentile_range: tuple or None, optional, default=None
        percentile range to investigate
        for numeric feature when grid_type='percentile'
    :param grid_range: tuple or None, optional, default=None
        value range to investigate
        for numeric feature when grid_type='equal'
    :param cust_grid_points: Series, 1d-array, list or None, optional, default=None
        customized list of grid points
        for numeric feature
    :param show_percentile: bool, optional, default=False
        whether to display the percentile buckets
        for numeric feature when grid_type='percentile'
    :param figsize: tuple or None, optional, default=None
        size of the figure, (width, height)
    :param ax: matplotlib Axes or None, optional, default=None
        if provided, plot on this Axes
    :param plot_params: dict or None, optional, default=None
        parameters for the plot


    Return:
    -------

    :return axes: matplotlib Axes
        Returns the Axes object with the plot for further tweaking
    """

    # check feature
    if type(feature) == str:
        if feature not in df.columns.values:
            raise ValueError('feature does not exist: %s' % feature)
        if sorted(list(np.unique(df[feature]))) == [0, 1]:
            feature_type = 'binary'
        else:
            feature_type = 'numeric'
    elif type(feature) == list:
        if len(feature) < 2:
            raise ValueError('one-hot encoding feature should contain more than 1 element')
        if not set(feature) < set(df.columns.values):
            raise ValueError('feature does not exist: %s' % str(feature))
        feature_type = 'onehot'
    else:
        raise ValueError('feature: please pass a string or a list (for onehot encoding feature)')

    # check percentile_range
    if percentile_range is not None:
        if len(percentile_range) != 2:
            raise ValueError('percentile_range: should contain 2 elements')
        if np.max(percentile_range) > 100 or np.min(percentile_range) < 0:
            raise ValueError('percentile_range: should be between 0 and 100')

    # check target values and calculate target rate through feature grids
    if type(target) == str:
        if target not in df.columns.values:
            raise ValueError('target does not exist: %s' % target)
        if sorted(list(np.unique(df[target]))) == [0, 1]:
            target_type = 'binary'
        else:
            target_type = 'regression'
    elif type(target) == list:
        if len(target) < 2:
            raise ValueError('multi-class target should contain more than 1 element')
        if not set(target) < set(df.columns.values):
            raise ValueError('target does not exist: %s' % (str(target)))
        for target_idx in range(len(target)):
            if sorted(list(np.unique(df[target[target_idx]]))) != [0, 1]:
                raise ValueError('multi-class targets should be one-hot encoded: %s' % (str(target[target_idx])))
        target_type = 'multi-class'
    else:
        raise ValueError('target: please pass a string or a list (for multi-class targets)')

    # create feature grids and bar counts
    useful_features = []
    if type(feature) == list:
        useful_features += feature
    else:
        useful_features.append(feature)
    if type(target) == list:
        useful_features += target
    else:
        useful_features.append(target)

    # prepare data for bar plot
    data = df[useful_features].copy()
    data_x, display_columns, percentile_columns = _prepare_data_x(
        feature=feature, feature_type=feature_type, data=data, num_grid_points=num_grid_points, grid_type=grid_type,
        percentile_range=percentile_range, grid_range=grid_range, cust_grid_points=cust_grid_points,
        show_percentile=show_percentile)

    data_x['fake_count'] = 1
    bar_data = data_x.groupby('x', as_index=False).agg({'fake_count': 'count'}).sort_values('x', ascending=True)

    # prepare data for target lines
    target_lines = []
    if target_type in ['binary', 'regression']:
        target_line = data_x.groupby('x', as_index=False).agg({target: 'mean'}).sort_values('x', ascending=True)
        target_lines.append(target_line)
    else:
        for target_idx in range(len(target)):
            target_line = data_x.groupby('x', as_index=False).agg(
                {target[target_idx]: 'mean'}).sort_values('x', ascending=True)
            target_lines.append(target_line)

    axes = _target_plot(
        feature_name=feature_name, display_columns=display_columns, percentile_columns=percentile_columns,
        target=target, bar_data=bar_data, target_lines=target_lines, figsize=figsize, ax=ax, plot_params=plot_params)
    return axes






