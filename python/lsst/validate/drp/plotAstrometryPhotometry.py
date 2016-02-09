#!/usr/bin/env python

# LSST Data Management System
# Copyright 2008-2016 AURA/LSST.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <https://www.lsstcorp.org/LegalNotices/>.

from __future__ import print_function, division

import matplotlib.pylab as plt
import numpy as np
import scipy.stats
from scipy.optimize import curve_fit

from .calcSrd import calcPA1, calcPA2, calcAM1

# Plotting defaults
plt.rcParams['axes.linewidth'] = 2
plt.rcParams['mathtext.default'] = 'regular'
plt.rcParams['font.size'] = 20
plt.rcParams['axes.labelsize'] = 20
# plt.rcParams['figure.titlesize'] = 30

color = {'all' : 'grey', 'bright' : 'blue', 
         'iqr' : 'green', 'rms' : 'red'}


def plotOutlinedLines(ax, x1, x2, x1_color=color['all'], x2_color=color['bright']):
    """Plot horizontal lines outlined in white.

    The motivation is to let horizontal lines stand out clearly 
    even against a cluttered background.
    """
    ax.axhline(x1, color='white', linewidth=4)
    ax.axhline(x2, color='white', linewidth=4)
    ax.axhline(x1, color=x1_color, linewidth=3)
    ax.axhline(x2, color=x2_color, linewidth=3)


def plotAstrometry(mag, mmagerr, mmagrms, dist, match, good_mag_limit=19.5,
                   plotbase=""):
    """Plot angular distance between matched sources from different exposures.

    @param[in] mag    Magnitude.  List or numpy.array.
    @param[in] mmagerr    Magnitude err.  List or numpy.array.
    @param[in] mmagrms    Magnitude RMS.  List or numpy.array.
    @param[in] dist   Separation from reference.  List of numpy.array
    @param[in] match  Number of stars matched.  Integer.
    """

    bright, = np.where(np.asarray(mag) < good_mag_limit)

    dist_median = np.median(dist) 
    bright_dist_median = np.median(np.asarray(dist)[bright])

    fig, ax = plt.subplots(ncols=2, nrows=1, figsize=(18, 12))

    ax[0].hist(dist, bins=100, color=color['all'],
               histtype='stepfilled', orientation='horizontal')
    ax[0].hist(np.asarray(dist)[bright], bins=100, color=color['bright'],
               histtype='stepfilled', orientation='horizontal',
               label='mag < %.1f' % good_mag_limit)

    ax[0].set_ylim([0., 500.])
    ax[0].set_ylabel("Distance [mas]")
    ax[0].set_title("Median : %.1f, %.1f mas" % 
                       (bright_dist_median, dist_median),
                       x=0.55, y=0.88)
    plotOutlinedLines(ax[0], dist_median, bright_dist_median)

    ax[1].scatter(mag, dist, s=10, color=color['all'], label='All')
    ax[1].scatter(np.asarray(mag)[bright], np.asarray(dist)[bright], s=10, 
                  color=color['bright'], 
                  label='mag < %.1f' % good_mag_limit)
    ax[1].set_xlabel("Magnitude")
    ax[1].set_ylabel("Distance [mas]")
    ax[1].set_xlim([17, 24])
    ax[1].set_ylim([0., 500.])
    ax[1].set_title("# of matches : %d, %d" % (len(bright), match))
    ax[1].legend(loc='upper left')
    plotOutlinedLines(ax[1], dist_median, bright_dist_median)

    plt.suptitle("Astrometry Check : %s" % plotbase.rstrip('_'), fontsize=30)
    plotPath = plotbase+"check_astrometry.png"
    plt.savefig(plotPath, format="png")


def expModel(x, a, b, norm):
    return a * np.exp(x/norm) + b


def magerrModel(x, a, b):
    return expModel(x, a, b, norm=5)


def plotExpFit(x, y, y_err, deg=2, ax=None, verbose=False):
    """Fit and plot an exponential quadratic to x, y, y_err.
    """

    if ax is None:
        ax = plt.figure()
        xlim = [10, 30]
    else:
        xlim = ax.get_xlim()

    popt, pcov = curve_fit(expModel, x, y, p0=[1, 0.02, 5], sigma=y_err)
    fit_params = popt
    x_model = np.linspace(*xlim, num=100)
    fit_model = expModel(x_model, *fit_params)
    label = '%.4g exp(mag/%.4g) + %.4g' % (fit_params[0], fit_params[2], fit_params[1])
    if verbose:  
        print(fit_params)
        print(label)

    ax.plot(x_model, fit_model, color='red',
            label=label)

    return fit_params


def plotMagerrFit(*args, **kwargs):
    plotExpFit(*args, **kwargs)


def plotPhotometry(mag, mmagerr, mmagrms, dist, match, good_mag_limit=19.5,
                   plotbase=""):
    """Plot photometric RMS for matched sources.

    @param[in] mag    Magnitude.  List or numpy.array.
    @param[in] mmagerr    Magnitude err.  List or numpy.array.
    @param[in] mmagrms    Magnitude RMS.  List or numpy.array.
    @param[in] dist   Separation from reference.  List of numpy.array
    @param[in] match  Number of stars matched.  Integer.
    """

    bright, = np.where(np.asarray(mag) < good_mag_limit)

    mmagrms_median = np.median(mmagrms) 
    bright_mmagrms_median = np.median(np.asarray(mmagrms)[bright])

    fig, ax = plt.subplots(ncols=2, nrows=2, figsize=(18, 16))
    ax[0][0].hist(mmagrms, bins=100, range=(0, 500), color=color['all'], label='All',
                  histtype='stepfilled', orientation='horizontal')
    ax[0][0].hist(np.asarray(mmagrms)[bright], bins=100, range=(0, 500), color=color['bright'], 
                  label='mag < %.1f' % good_mag_limit,
                  histtype='stepfilled', orientation='horizontal')
    ax[0][0].set_ylim([0, 500])
    ax[0][0].set_ylabel("RMS [mmag]")
    ax[0][0].set_title("Median : %.1f, %.1f mmag" % 
                    (bright_mmagrms_median, mmagrms_median),
                    x=0.55, y=0.88)
    plotOutlinedLines(ax[0][0], mmagrms_median, bright_mmagrms_median)

    ax[0][1].scatter(mag, mmagrms, s=10, color=color['all'], label='All')
    ax[0][1].scatter(np.asarray(mag)[bright], np.asarray(mmagrms)[bright], 
                     s=10, color=color['bright'], 
                     label='mag < %.1f' % good_mag_limit)

    ax[0][1].set_xlabel("Magnitude")
    ax[0][1].set_ylabel("RMS [mmag]")
    ax[0][1].set_xlim([17, 24])
    ax[0][1].set_ylim([0, 500])
    ax[0][1].set_title("# of matches : %d, %d" % (len(bright), match))
    ax[0][1].legend(loc='upper left')
    plotOutlinedLines(ax[0][1], mmagrms_median, bright_mmagrms_median)

    ax[1][0].scatter(mmagrms, mmagerr, s=10, color=color['all'], label='All')
    ax[1][0].scatter(np.asarray(mmagrms)[bright], np.asarray(mmagerr)[bright], 
                     s=10, color=color['bright'], 
                     label='mag < %.1f' % good_mag_limit)
    ax[1][0].set_xscale('log')
    ax[1][0].set_yscale('log')
    ax[1][0].plot([0, 1000], [0, 1000], 
                  linestyle='--', color='black', linewidth=2)
    ax[1][0].set_xlabel("RMS of Quoted Magnitude [mmag]")
    ax[1][0].set_ylabel("Median Quoted Magnitude Err [mmag]")
    ax[1][0].set_xlim([1, 500])
    ax[1][0].set_ylim([1, 500])

    ax[1][1].scatter(mag, mmagerr, color=color['all'], label=None)
    ax[1][1].set_yscale('log')
    ax[1][1].scatter(np.asarray(mag)[bright], np.asarray(mmagerr)[bright],
                     s=10, color=color['bright'],
                     label=None,
                     )
    ax[1][1].set_xlabel("Magnitude [mag]")
    ax[1][1].set_ylabel("Median Quoted Magnitude Err [mmag]")
    ax[1][1].set_xlim([17, 24])
    ax[1][1].set_ylim([1, 500])

    w, = np.where(mmagerr < 200)
    plotMagerrFit(mag[w], mmagerr[w], mmagerr[w], ax=ax[1][1])
    ax[1][1].legend(loc='upper left')

    plt.suptitle("Photometry Check : %s" % plotbase.rstrip('_'), fontsize=30)
    plotPath = plotbase+"check_photometry.png"
    plt.savefig(plotPath, format="png")


def plotPA1(gv, magKey, plotbase=""):
    pa1 = calcPA1(gv, magKey)

    diff_range = (-100, +100)

    fig = plt.figure(figsize=(18,12))
    ax1 = fig.add_subplot(1,2,1)
    ax1.scatter(pa1.means, pa1.diffs, s=10, color=color['bright'], linewidth=0)
    ax1.axhline(+pa1.rms, color=color['rms'], linewidth=3)
    ax1.axhline(-pa1.rms, color=color['rms'], linewidth=3)
    ax1.axhline(+pa1.iqr, color=color['iqr'], linewidth=3)
    ax1.axhline(-pa1.iqr, color=color['iqr'], linewidth=3)

    ax2 = fig.add_subplot(1,2,2, sharey=ax1)
    ax2.hist(pa1.diffs, bins=25, range=diff_range,
             orientation='horizontal', histtype='stepfilled',
             normed=True, color=color['bright'])
    ax2.set_xlabel("relative # / bin")

    yv = np.linspace(diff_range[0], diff_range[1], 100)
    ax2.plot(scipy.stats.norm.pdf(yv, scale=pa1.rms), yv, 
             marker='', linestyle='-', linewidth=3, color=color['rms'],
             label="PA1(RMS) = %4.2f mmag" % pa1.rms)
    ax2.plot(scipy.stats.norm.pdf(yv, scale=pa1.iqr), yv, 
             marker='', linestyle='-', linewidth=3, color=color['iqr'],
             label="PA1(IQR) = %4.2f mmag" % pa1.iqr)
    ax2.set_ylim(*diff_range)
    ax2.legend()
#    ax1.set_ylabel(u"12-pixel aperture magnitude diff (mmag)")
#    ax1.set_xlabel(u"12-pixel aperture magnitude")
    ax1.set_xlabel("psf magnitude")
    ax1.set_ylabel("psf magnitude diff (mmag)")
    for label in ax2.get_yticklabels(): label.set_visible(False)

    plt.suptitle("PA1: %s" % plotbase.rstrip('_'))
    plotPath = "%s%s" % (plotbase, "PA1.png")
    plt.savefig(plotPath, format="png")


def plotAM1(rmsDistMAS, D, Annulus, magBinLow, magBinHigh, plotbase=""): 

    if not rmsDistMAS:
        print('No objects in given mag bins at requested separation in the same visit!')
        return

    rmsRelSep = np.median(rmsDistMAS)
    AM1 = 10.0
    AD1 = 20.0
    AF1 = 10.0
    pCentOver = 0
    for val in rmsDistMAS:
        if (val > AM1+AD1):
            pCentOver += 1
    pCentOver /= float(len(rmsDistMAS))
    pCentOver *= 100.0

    fig = plt.figure(figsize=(10,6))
    ax1 = fig.add_subplot(1,1,1)
    ax1.hist(rmsDistMAS, bins=25, range=(0.0, 100.0),
             histtype='stepfilled',
             label='D: %.1f-%.1f arcmin\nMag Bin: %.1f-%.1f' % 
                   (D-Annulus, D+Annulus, magBinLow, magBinHigh))
    ax1.axvline(rmsRelSep, 0, 1, linewidth=2,  color='black', 
                label='median RMS of relative\nseparation: %.2f mas' % (rmsRelSep))
    ax1.axvline(AM1, 0, 1, linewidth=2, color='red', 
                label='AM1: %.2f mas' % (AM1))
    ax1.axvline(AM1+AD1, 0, 1, linewidth=2, color='green',
                label='AM1+AD1: %.2f mas\nAF1: %2.f%% > AM1+AD1 = %2.f%%' % (AM1+AD1, AF1, pCentOver))

    ax1.set_title('Number of RMS Rel Distances: %d' % len(rmsDistMAS))
    ax1.set_xlim(0.0,100.0)
    ax1.set_xlabel('rms Relative Separation (mas)')
    ax1.set_ylabel('# pairs / bin')

    ax1.legend(loc='upper right', fontsize=16)

    figName = plotbase+'D_%d_ARCMIN_%.1f-%.1f.png' % (int(D), magBinLow, magBinHigh)
    plt.savefig(figName,dpi=300)
