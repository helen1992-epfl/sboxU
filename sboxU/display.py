#!/usr/bin/sage
# Time-stamp: <2018-02-06 15:52:10 lperrin>

import matplotlib.pyplot as plt
from diff_lin import *
from math import log
from collections import defaultdict

# source for color sequence: https://matplotlib.org/users/dflt_style_changes.html

COLOR_SEQUENCE = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]



# !SECTION! Display in the console 

def pretty_spectrum(d):
    """Returns a line containing a pretty representation of the
    dictionnary d.

    """
    if len(d.keys()) == 0:
        return "{}"
    line = "{"
    for k in sorted(d.keys()):
        line += "{}: {}, ".format(k, d[k])
    return line[:-2] + "}"


def pretty_vector(v, template="{:x}"):
    """Returns a string containing the representation of the integers in v
    using the template given (defaults to a simple decimal
    representation).

    """
    if len(v) == 0:
        return "[]"
    line = "["
    for x in v:
        line += template.format(x) + ","
    return line[:-1] + "]"


# !SECTION! Graph generation

def plot_table_averages(l,
                        file_name="avg",
                        rows=True,
                        cols=True,
                        col_rows=None,
                        col_cols=None):
    if rows and cols:
        col_rows, col_cols = COLOR_SEQUENCE[0], COLOR_SEQUENCE[1]
    elif rows:
        col_rows = COLOR_SEQUENCE[0]
    elif cols:
        col_cols = COLOR_SEQUENCE[0]
    else:
        raise "At least rows or cols should be set to True!"
    fig, p = plt.subplots(figsize=(15,10))
    p.set_xlabel('row/column index')
    p.set_ylabel('Average of the absolute value')
    # rows
    if rows:
        avgs_a = []
        for a in xrange(1, len(l)):
            avg = 0.0
            for w in l[a]:
                avg += abs(float(w))
            avg = avg/len(l[a])
            avgs_a.append(avg)
        p.plot(range(1, len(avgs_a)+1),
               avgs_a,
               marker="o",
               color=col_rows,
               linestyle="-",
               markersize=2,
               label="Rows")
    # columns
    if cols:
        avgs_b = []
        for b in xrange(1, len(l)):
            avg = 0.0
            col = [l[a][b] for a in xrange(0, len(l))]
            for w in col:
                avg += abs(float(w))
            avg = avg/len(col)
            avgs_b.append(avg)
        p.plot(range(1, len(avgs_b)+1),
               avgs_b,
               color=col_cols,
               marker="^",
               linestyle="-",
               markersize=2,
               label="Columns")
    # finalizing graph
    legend = p.legend(loc='upper right', shadow=True)
    p.set_xlim([0, len(l)])
    fig.savefig("{}.png".format(file_name))


def plot_table_variances(l,
                        file_name="var",
                        rows=True,
                        cols=True,
                        col_rows=None,
                        col_cols=None):
    if rows and cols:
        col_rows, col_cols = COLOR_SEQUENCE[0], COLOR_SEQUENCE[1]
    elif rows:
        col_rows = COLOR_SEQUENCE[0]
    elif cols:
        col_cols = COLOR_SEQUENCE[0]
    else:
        raise "At least rows or cols should be set to True!"
    fig, p = plt.subplots(figsize=(15,10))
    p.set_xlabel('row/column index')
    p.set_ylabel('Variance of the absolute value')
    # rows
    if rows:
        variances_a = []
        for a in xrange(1, len(l)):
            avg = 0.0
            for w in l[a]:
                avg += abs(float(w))
            avg = avg/len(l[a])
            v = 0.0
            for w in l[a]:
                v += (abs(w) - avg)**2
            v = v / float(len(l[a]))
            variances_a.append(v)
        p.plot(range(1, len(variances_a)+1),
               variances_a,
               marker="o",
               color=col_rows,
               linestyle="-",
               markersize=2,
               label="Rows")
    # columns
    if cols:
        variances_b = []
        for b in xrange(1, len(l)):
            avg = 0.0
            col = [l[a][b] for a in xrange(0, len(l))]
            for w in col:
                avg += abs(float(w))
            avg = avg/len(col)
            v = 0.0
            for w in col:
                v += (abs(w) - avg)**2
            v = v / float(len(col))
            variances_b.append(v)
        p.plot(range(1, len(variances_b)+1),
               variances_b,
               color=col_cols,
               marker="o",
               linestyle="-",
               markersize=2,
               label="Columns")
    # finalizing graph
    legend = p.legend(loc='upper right', shadow=True)
    p.set_xlim([0, len(l)])
    fig.savefig("{}.png".format(file_name))


def plot_differential(dict_s,
                      file_name="differential",
                      with_random_permutation=True,
                      with_random_function=False,
                      u_max=12,
                      x_log_scale=False,
                      y_log_scale=True):
    # distribution is the same for random functions and permutations
    with_random = with_random_function or with_random_permutation
    # coeff probabilities for s
    spectra = {}
    for func_name in dict_s.keys():
        spectra[func_name] = defaultdict(float)
        s = dict_s[func_name]
        diff_spec = differential_spectrum(s)
        for k in diff_spec.keys():
            spectra[func_name][k] = float(diff_spec[k]) / (len(s) * (len(s) - 1))
    # coeff probabilities for random function
    n = float(log(len(s), 2))
    if with_random:
        spectra["Random Permutation"] = {
            c: ddt_coeff_probability(n, n, c)
            for c in xrange(0, u_max+1, 2)
        }
    # plotting
    abscissa = range(0, u_max+1, 2)
    fig, p = plt.subplots(figsize=(15,10))
    p.set_xlabel('DDT coefficients')
    p.set_ylabel('Number of occurrences')
    if x_log_scale:
        p.set_xscale("log", nonposx="clip")
    if y_log_scale:
        p.set_yscale("log", nonposy="clip")
    color_index = 0
    for w in spectra.keys():
        ordenna = []
        for c in xrange(0, u_max+1, 2):
            if c in spectra[w].keys():
                ordenna.append(float(spectra[w][c]))
            else:
                ordenna.append(0.0)
        p.plot(abscissa,
               ordenna,
               color=COLOR_SEQUENCE[color_index],
               marker="o",
               linestyle="-",
               markersize=2,
               label=w)
        color_index +=1
        legend = p.legend(loc='upper right', shadow=True)
    p.set_xlim([0, u_max])
    fig.savefig("{}.png".format(file_name))
    
        

def plot_linear(dict_s,
                file_name="linear",
                with_random_permutation=True,
                with_random_function=False,
                l_min=0,
                l_max=64,
                x_log_scale=False,
                y_log_scale=True):
    # coeff probabilities for s
    spectra = {}
    for func_name in dict_s.keys():
        spectra[func_name] = defaultdict(float)
        s = dict_s[func_name]
        walsh_spec = walsh_spectrum(s)
        for k in walsh_spec.keys():
            if k == 0:
                spectra[func_name][k] = float(walsh_spec[k]) / (len(s) * (len(s) - 1))
            else:
                spectra[func_name][abs(k)] += float(walsh_spec[k]) / (len(s) * (len(s) - 1))
    # coeff probabilities for random functions
    n = float(log(len(s), 2))
    if with_random_function:
        spectra["Random Function"] = {
            c: lat_coeff_probability_function(n, n, c)
            for c in xrange(l_min, l_max+1, 4)
        }
    n = float(log(len(s), 2))
    if with_random_permutation:
        spectra["Random Permutation"] = {
            c: lat_coeff_probability_permutation(n, n, c)
            for c in xrange(l_min, l_max+1, 4)
        }
    # plotting
    abscissa = range(l_min, l_max+1, 4)
    fig, p = plt.subplots(figsize=(15,10))
    p.set_xlabel('abs(LAT coefficients)')
    p.set_ylabel('Number of occurrences')
    color_index = 0
    for w in spectra.keys():
        ordenna = []
        for c in xrange(l_min, l_max+1, 4):
            if c in spectra[w].keys():
                ordenna.append(float(spectra[w][c]))
            else:
                ordenna.append(0.0)
        p.plot(abscissa,
               ordenna,
               color=COLOR_SEQUENCE[color_index],
               marker="o",
               linestyle="-",
               markersize=2,
               label=w)
        color_index +=1
        legend = p.legend(loc='upper right', shadow=True)
    p.set_xlim([l_min, l_max])
    if x_log_scale:
        p.set_xscale("log", nonposx="clip")
    if y_log_scale:
        p.set_yscale("log", nonposy="clip")
    fig.savefig("{}.png".format(file_name))


# !SECTION! Jackson Pollock

def save_pollock(mat,
                 color_scheme="CMRmap_r",
                 name="pollock",
                 vmin=0,
                 vmax=20,
                 folder=None,
                 frame=True,
                 axes=False,
                 colorbar=False):
    fig, p = plt.subplots(figsize=(15,15))
    abs_mat = [[abs(mat[i][j]) for j in xrange(0, len(mat[0]))]
               for i in xrange(0, len(mat))]
    axes = p.imshow(
        abs_mat,
        interpolation="None",
        cmap=plt.cm.get_cmap(color_scheme, 100),
        vmin=vmin,
        vmax=vmax
    )
    p.set_aspect('equal')
    p.get_xaxis().set_visible(axes)
    p.get_yaxis().set_visible(axes)
    p.patch.set_alpha(0)
    p.set_frame_on(frame)
    # if colorbar:
    #     axes.colorbar(p, orientation='vertical')
    if folder == None:
        name_base = "{}.png"
    else:
        name_base = folder + "/{}.png"
    fig.savefig(name_base.format(name))