######################################################################
#                                                                    #
#  Plotter.py                                                        #
#  Author: Jenna Chisholm                                            #
#  Updated: Mar.1/23                                                 #
#                                                                    #
#  Defines classes for observables, particles, and datasets, as      #
#  well as a plotting class with functions for plotting truth vs.    #
#  reco histograms, confusion matrices, resolution histograms, and   #
#  plots of resolution as a function of a specified variable.        #
#  Intended for visualizing and comparing the results of different   #
#  ttbar reconstruction results.                                     # 
#                                                                    #
#  Thoughts for improvements: Include systematics, allow pt cuts     #
#  for truth vs reco and confusion matrices, maybe better color      #
#  scheme handling (e.g. with cuts on the data).                     #
#                                                                    #
######################################################################


# Import useful packages
import pandas as pd
#import awkward as ak
import numpy as np
#import matplotlib
#matplotlib.use('Agg')  # need for not displaying plots when running batch jobs
from matplotlib import pyplot as plt
from matplotlib import colors
#from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, plot_confusion_matrix
from scipy.stats import norm
from scipy.stats import cauchy
from sigfig import round
from analysis import Analysis


class Observable:
    """
    Observable object class (for plotting purposes)
    """

    def __init__(self, name, label, ticks, unit='', res='Resolution', alt_names=[]):
        """
        Initializes a observable object.

            Parameters:
                name (str): Name of the observable (e.g.'pt')
                label (str): Label for the observable (note: this may be different than the name if you want to, for example, use Latex formatting).
                ticks (np.array): Numpy array of where you want the axes ticks placed.

            Options:
                unit (str): Units for the observable, for axis title purposes (e.g.'[GeV]', default:'').
                res (str): Specifies whether this observable should use 'Resolution' or 'Residuals' (default:'Resolution').
                alt_names (list of str): Alternate names for the observable (default: []).

            Attributes:
                name (str): Name of the observable (e.g.'pt')
                label (str): Label for the observable (note: this may be different than the name if you want to, for example, use Latex formatting).
                ticks (np.array): Numpy array of where you want the axes ticks placed.
                unit (str): Units for the observable, for axis title purposes (e.g.'[GeV]', default:'').
                alt_names (list of str): Alternate names for the observable (default: []).
                tick_labels (list): Labels for the ticks (note: these are specially specified, since sometimes one might want an infinity symbol or such)

        """

        self.name = name
        self.label = label
        self.unit = unit if unit=='' else '['+unit+']'
        self.res = res.capitalize()
        self.ticks = ticks
        self.alt_names = alt_names

        tick_labels = [str(x) for x in ticks]
        tick_labels[0] = '-'+r'$\infty$' if name in ['eta','y','yboost','ystar'] else tick_labels[0]
        tick_labels[-1] = r'$\infty$' if name!='phi' else tick_labels[-1]
        self.tick_labels = tick_labels


class Particle:
    """ 
    Particle object class (for plotting purposes)
    """
    
    def __init__(self, name, label, observables, alt_names=[]):
        """
        Initializes a particle object. 

            Parameters:
                name (str): Name of the particle (e.g.'th')
                label (str): Label for the particle (note: this may be different than the name if you want to, for example, use Latex formatting).
                observables (list of observable objects): List of observable objects that one could plot for this particle.

            Options:
                alt_names (list of str): Alternate names for the particle (default: []).

            Attributes:
                name (str): Name of the particle (e.g.'th').
                observables (list of observable objects): List of observable objects that one could plot for this particle.
                labels (dictionary of strings): Dictionary of the axis labels for each observable for this particle.
                labels_nounits (dictionary of strings): Dictionary of the axis labels for each observable for this particle WITHOUT units.
                alt_names (list of str): Alternate names for the particle (default: []).
        """

        self.name = name
        self.observables = observables
        self.alt_names = alt_names

        var_names = [var.name for var in observables]
        labels = ['$'+var.label+'^{'+label+'}$ '+var.unit for var in observables]
        labels_nounits = ['$'+var.label+'^{'+label+'}$' for var in observables]
        self.labels = dict(zip(var_names,labels))
        self.labels_nounits = dict(zip(var_names,labels_nounits))


class Dataset:
    """ 
    Dataset object class
    """

    def __init__(self, df, reco_method, data_type, color, cuts='No Cuts', perc_events=100,sysUP_df=pd.DataFrame(),sysDOWN_df=pd.DataFrame(), shortname=''):
        """
        Initializes a dataset object.

            Parameters:
                df (pd.DataFrame): Pandas DataFrame full of data.
                reco_method (str): Reconstruction method (e.g.'KLFitter').
                data_type (str): Level and muon type (e.g.'parton_ejets').
                color (str): Color identifier for the plots.
            
            Options:
                cuts (str): Specify the cuts that were made on this dataset (default: 'No Cuts').
                perc_events (float or double or int): Percentage of the total number of events in this dataset (default: 100).
                sysUP_df (pd.DataFrame): Dataframe for up systematics (default: empty dataframe).
                sysDOWN_df (pd.DataFrame) (arr of datasets): Dataframe for down systematics (default: empty dataframe).
                shortname (str): Shorthand name for the reconstruction method, to be used in plot legends (default: <reco_method>).
            
            Attributes:
                df (pd.DataFrame): Pandas DataFrame full of data.
                reco_method (str): Reconstruction method (e.g.'KLFitter').
                data_type (str): Level and muon type (e.g.'parton_ejets').
                cuts (str): Specifies the cuts that were made on this dataset (e.g. 'LL>-52').
                perc_events (float or double or int): Fraction of the total number of events in this dataset.
        """

        self.df = df
        self.reco_method = reco_method
        self.data_type = data_type
        self.color = color
        self.cuts = cuts
        self.perc_events = perc_events
        self.sysUP_df = sysUP_df
        self.sysDOWN_df = sysDOWN_df
        self.shortname = reco_method if shortname=='' else shortname

        if self.perc_events==100 and self.cuts!='No Cuts': 
            print('WARNING: Do you really have 100\% of events if you are making cuts?')

        if (sysUP_df.empty and not sysDOWN_df.empty) or (not sysUP_df.empty and sysUP_df.empty):
            print('Please include both up and down sets of systematics to include in plots.')


class Plot:
    """ 
    A class for making various kinds of plots

        Methods:
            TruthReco_Hist: Creates and saves a histogram with true and reconstructed data both plotted, for a given dataset, particle, and observable.
            Confusion_Matrix: Creates and saves a 2D histogram of true vs reconstructed data, normalized across rows, for a given dataset, particle, and observable.
            Sys_Hist: Creates and saves a histogram of the systematics for all datasets provided, for a given particle and observable.
            Res_Hist: Creates and saves a resolution (or residual) histogram all datasets provided, for a given particle and observable.
            Res_vs_Var: Creates and saves a plot of resolution (or residual) for a given observable against another (or the same) given observable, for all datasets provided, for a given particle.

    """

    def TruthReco_Hist(dataset,particle,observable,save_loc='./',nbins=30):
        """
        Creates and saves a histogram with true and reconstructed data both plotted, for a given dataset, particle, and observable.

            Parameters:
                dataset (Dataset object): Dataset object of the data you want to plot.
                particle (Particle object): Particle object of the particle you want to plot.
                observable (Observable object): Observable object of the observable you want to plot.

            Options:
                save_loc (str): Directory where you want the histogram saved to (default: current directory)
                nbins (int): Number of desired bins for the histogram (default: 30).

            Returns:
                Saves histogram in <save_loc> as '<reco_method>_TruthReco_Hist_<data_type>_<particle>_<observable>.png' .
        """

        # Get the dataframe for this dataset
        df = dataset.df

        # Define a useful string
        name = particle.name+'_'+observable.name

        # Set the range (based on observable and particle we're plotting)
        ran = observable.ticks[::len(observable.ticks)-1]

        # Plot histograms of true and reco results on the same histogram
        fig, (ax1, ax2) = plt.subplots(nrows=2,sharex=True,gridspec_kw={'height_ratios': [4, 1]})
        truth_n, _, _ = ax1.hist(df['truth_'+name],bins=nbins,range=ran,histtype='step',label='truth',color='black')
        reco_n, bins, _ = ax1.hist(df['reco_'+name],bins=nbins,range=ran,histtype='step',label='reco',color=dataset.color)
        
        # Make sure histograms aren't getting cut off
        max_truth = max(truth_n)*1.05
        max_reco = max(reco_n)*1.05
        ax1.set(ylim=(0,max([max_truth,max_reco])))

        # Plot the ratio of the two histograms underneath (with a dashed line at 1)
        x_dash,y_dash = np.linspace(min(ran),max(ran),100),[1]*100
        ax2.plot(x_dash,y_dash,'r--')
        bin_width = np.diff(bins)
        ax2.plot(bins[:-1]+bin_width/2, truth_n/reco_n,'ko')  # Using bin width so points are plotting aligned with middle of the bin
        ax2.set(ylim=(0, 2))
        #ax2.set_yscale('log')

        # Set some axis labels
        ax2.set_xlabel(particle.labels[observable.name])
        ax1.set_ylabel('Counts')
        ax2.set_ylabel('Ratio (truth/reco)')
        ax1.legend()
        
        # Save the figure as a png in save location
        fig_name = dataset.reco_method+'('+dataset.cuts+')_TruthReco_Hist_'+dataset.data_type+'_'+name
        plt.savefig(save_loc+fig_name,bbox_inches='tight')
        print('Saved Figure: '+fig_name)

        plt.close()

    
    def Confusion_Matrix(dataset,particle,observable,norm=True,save_loc='./',text_color='k',pt_low=None,pt_high=None):
        """ 
        Creates and saves a 2D histogram of true vs reconstructed data, normalized across rows, for a given dataset, particle, and observable.

            Parameters:
                dataset (Dataset object): Dataset object of the data you want to plot.
                particle (Particle object): Particle object of the particle you want to plot.
                observable (Observable object): Observable object of the observable you want to plot.
            
            Options:
                norm (bool): Whether or not to normalize the confusion matrix across rows (default: True).
                save_loc (str): Directory where you want the histogram saved to (default: current directory).
                text_color (str): Desired text color for the percentages written on the histogram (default: black or 'k').
                pt_low (int): Lower edge for the range of pt you'd like to look at (non-inclusive) (default: None).
                pt_high (int): Upper edge for the range of pt you'd like to look at (non-inclusive) (default: None).


            Returns:
                Saves histogram in <save_loc> as '<reco_method>_Confusion_Matrix_<data_type>_<particle>_<observable>.png'. 
        """

        # Make the appropriate color map
        color_map=colors.LinearSegmentedColormap.from_list('my_cmap', ['white', dataset.color])


        # Define a useful string
        name =particle.name+'_'+observable.name

        # Define useful constants
        tk = observable.ticks
        tkls = observable.tick_labels
        
        # Get the dataframe for this dataset
        df = dataset.df

        # Cut to specified pt range, if desired
        if pt_low!=None:
            df = df[df['truth_'+particle.name+'_pt']>pt_low]
        if pt_high!=None:
            df = df[df['truth_'+particle.name+'_pt']<pt_high]

        # Creating pt tag for later saving/naming
        if pt_low!=None and pt_high!=None:
            pt_tag = '('+str(pt_low)+'<p_T<'+str(pt_high)+')'
            #if observable.name=='pt':
            #    tks = np.linspace(pt_low,pt_high,11)
            #    tkls = [str(x) for x in tks]
        elif pt_low!=None:
            pt_tag = '(p_T>'+str(pt_low)+')'
            #if observable.name=='pt':
            #    tks = np.linspace(pt_low,pt_low+250,11)
            #    tkls = [str(x) for x in tks]
            #    tkls[-1] = r'$\infty$'
        elif pt_high!=None:
            pt_tag = '(p_T<'+str(pt_high)+')'
            #if observable.name=='pt':
            #    tks = np.linspace(0,pt_high,11)
            #    tkls = [str(x) for x in tks]
        else:
            pt_tag=''


        n = len(tk)
        ran = tk[::n-1]



        # Create 2D array of truth vs reco observable (which can be plotted also)
        H, _, _, _ = plt.hist2d(np.clip(df['reco_'+name],tk[0],tk[-1]),np.clip(df['truth_'+name],tk[0],tk[-1]),bins=tk,range=[ran,ran])

        # Normalize across rows (if desired)
        if norm:
            H = np.divide(H,np.sum(H,axis=0),where=np.sum(H,axis=0)!=0)  # This should ensure we're not dividing by zero
            H = H*100
            #H = (H/np.sum(H,axis=0))*100  # Old way
        
        # Round to integers (and transpose, so it's where we need it for plotting later)
        cm = np.rint(H).T.astype(int)

        # Plot truth vs reco pt with normalized rowsx
        plt.figure(dataset.data_type+' '+particle.name+' '+observable.name+' Normalized 2D Plot')
        masked_cm = np.ma.masked_where(cm==0,cm)  # Needed to make the zero bins white
        plt.imshow(masked_cm,extent=[0,n-1,0,n-1],cmap=color_map,origin='lower')
        plt.xticks(np.arange(n),tkls,fontsize=9,rotation=-25)
        plt.yticks(np.arange(n),tkls,fontsize=9)
        plt.xlabel('Reco-level '+particle.labels[observable.name])
        plt.ylabel('Parton-level '+particle.labels[observable.name])
        if norm: plt.clim(0,100)
        plt.colorbar()

        # Label the content of each bin
        for j in range (n-1):
            for k in range(n-1):
                if masked_cm.T[j,k] != 0:   # Don't label empty bins
                    plt.text(j+0.5,k+0.5,masked_cm.T[j,k],color=text_color,fontsize=6,weight="bold",ha="center",va="center")

        # Save the figure in save location as a png
        fig_name = dataset.reco_method+'('+dataset.cuts+')_Confusion_Matrix_'+dataset.data_type+'_'+name+pt_tag
        plt.savefig(save_loc+fig_name,bbox_inches='tight')
        print('Saved Figure: '+fig_name)

        plt.close()




    def Sys_Hist(datasets,particle,observable,save_loc='./',nbins=5):
        """
        Creates and saves a histogram of the systematics for all datasets provided, for a given particle and observable.

            Parameters:
                datasets (list of Dataset objects): List of dataset objects of the datasets you want to plot.
                particle (Particle object): Particle object of the particle you want to plot.
                observable (observable object): Observable object of the observable you want to plot.

            Options:
                save_loc (str): Directory where you want the histogram saved to (default: current directory).
                nbins (int): Number of desired bins for the histogram (default: 5).

            Returns:
                Saves histogram in <save_loc> as '<res>_<data_type>_<particle>_<observable>.png'.                
        """

        # Define a useful string
        name = particle.name+'_'+observable.name

        # Set the range (based on observable and particle we're plotting)
        ran = observable.ticks[::len(observable.ticks)-1]

        # Create the figure for the systematics histogram
        plt.figure('Sys')

        # Go through and plot each of the datasets
        for dataset in datasets:

            # Create a temporary plot to bin the data (set density=True to normalize the counts)
            plt.figure('Temporary')
            reco_n, bins, _ = plt.hist(dataset.df['reco_'+name],bins=nbins,range=ran,density=True)
            sysUP_n, _, _ = plt.hist(dataset.sysUP_df['sysUP_'+name],bins=nbins,range=ran,density=True)
            sysDOWN_n, _, _ = plt.hist(dataset.sysDOWN_df['sysDOWN_'+name],bins=nbins,range=ran,density=True)
            plt.close('Temporary')

            # Calculate the up and down fractional uncertainties
            sysUP_results = np.array([100*(up-nom)/nom for up,nom in zip(sysUP_n,reco_n)])
            sysDOWN_results = np.array([100*(nom-down)/nom for down,nom in zip(sysDOWN_n,reco_n)])

            # Grab the bin width (not sure if there's somewhere easier to get this, like stored in the observables...)
            bin_width = np.diff(bins)

            # Switch back to the systematics figure (do I need this?)
            plt.figure('Sys')
            #plt.bar(x=bins[:-1],height=sysUP_results,width=np.diff(bins),align='edge',fill=True,linewidth=1,color='r',edgecolor='r',alpha=0.5,zorder=-1,label='up')
            #plt.bar(x=bins[:-1],height=sysDOWN_results,width=np.diff(bins),align='edge',fill=True,linewidth=1,color='b',edgecolor='b',alpha=0.5,zorder=-1,label='down')
            plt.hist(bins[:-1], bins, weights=sysUP_results, histtype='step', color=dataset.color, linestyle='dotted')
            plt.hist(bins[:-1], bins, weights=sysDOWN_results, histtype='step', color=dataset.color, label=dataset.reco_method+': '+dataset.cuts+' ('+str(dataset.perc_events)+'%)')

            # Need to sort systematics into which one is on top and which one is on bottom -- if both are on the same side of zero, just use the bigger one
            #pos_weights = np.array([max(up,down) if max(up,down)>0 else 0 for up, down in zip(sysUP_results,sysDOWN_results)])
            #neg_weights = np.array([min(up,down) if min(up,down)<0 else 0 for up, down in zip(sysUP_results,sysDOWN_results)])

            # Plot the fractional uncertainties
            #plt.hist(bins[:-1], bins, weights=pos_weights, histtype='step', color=dataset.color, label=dataset.reco_method+': '+dataset.cuts+' ('+str(dataset.perc_events)+'%)')
            #plt.hist(bins[:-1], bins, weights=neg_weights, histtype='step', color=dataset.color)


        # Draw a dashed line at zero
        x_dash, y_dash = np.linspace(min(ran),max(ran),nbins),[0]*nbins
        plt.plot(x_dash,y_dash,'k--')

        # Set some axis labels
        plt.xlabel(particle.labels[observable.name])
        plt.ylabel('Fractional Uncertainty [%]')
        plt.legend(prop={'size': 6})

        # Save the figure as a png in save location
        fig_name = 'Systematics_'+dataset.data_type+'_'+name
        plt.savefig(save_loc+fig_name,bbox_inches='tight')
        print('Saved Figure: '+fig_name)

        plt.close()









    def Res_Hist(datasets,particle,observable,save_loc='./',nbins=30,core_fit='nofit',include_moments=False,pt_low=None,pt_high=None):
        """
        Creates and saves a resolution (or residual) plot all datasets provided, for a given particle and observable.

            Parameters:
                datasets (list of Dataset objects): List of dataset objects of the datasets you want to plot.
                particle (Particle object): Particle object of the particle you want to plot.
                observable (Observable object): Observable object of the observable you want to plot.

            Options:
                save_loc (str): Directory where you want the histogram saved to (default: current directory).
                nbins (int): Number of desired bins for the histogram (default: 30).
                core_fit (str): Type of fit you want to use for the datasets (default: 'nofit', other options: 'gaussian' or 'cauchy').
                include_moments (bool): Whether or not to include the mean and standard deviation in the legend.
                pt_low, pt_high (int): Lower and upper edges for the range of pt you'd like to look at (non-inclusive).

            Returns:
                Saves histogram in <save_loc> as '<res>_<data_type>_<particle>_<observable>.png'.
        """

        # Define a useful string
        name =particle.name+'_'+observable.name

        # Create figure to be filled
        plt.figure(name+' '+'Res')
        
        # Fill figure with data
        for dataset in datasets:
            
            # Get dataframe
            df = dataset.df

            # Creating pt tag for later saving/naming
            if pt_low!=None and pt_high!=None:
                pt_tag = '('+str(pt_low)+'<p_T<'+str(pt_high)+')'
            elif pt_low!=None:
                pt_tag = '(p_T>'+str(pt_low)+')'
            elif pt_high!=None:
                pt_tag = '(p_T<'+str(pt_high)+')'
            else:
                pt_tag=''

            # Cut to specified pt range, if desired
            if pt_low!=None:
                df = df[df['truth_'+particle.name+'_pt']>pt_low]
            if pt_high!=None:
                df = df[df['truth_'+particle.name+'_pt']<pt_high]

        
            # Calculate the resolution (or residuals), and wrap phi if that's what we're dealing with
            res = observable.res
            if res=='Resolution':
                if observable.name=='phi':
                    df['res_'+name] = Analysis.wrap_phi((df['reco_'+name] - df['truth_'+name]))/df['truth_'+name]
                else:
                    df['res_'+name] = (df['reco_'+name] - df['truth_'+name])/df['truth_'+name]
            else:
                if observable.name=='phi':
                    df['res_'+name] = Analysis.wrap_phi(df['reco_'+name] - df['truth_'+name])
                else:
                    df['res_'+name] = df['reco_'+name] - df['truth_'+name]

            # Calculate mean and standard deviation of the resolution
            if include_moments==True:
                res_mean = round(df['res_'+name].mean(),sigfigs=2)
                res_std = round(df['res_'+name].std(),sigfigs=2)
                mom_tag = '\n$\mu=$'+str(res_mean)+', $\sigma=$'+str(res_std)
            else:
                mom_tag = ''


            # Plot the resolution
            plt.hist(df['res_'+name],bins=nbins,range=(-1,1),histtype='step',label=dataset.shortname+': '+dataset.cuts+' ('+str(dataset.perc_events)+'%)'+mom_tag,density=True,color=dataset.color)

            # If we want to fit the core distribution and get that mean and standard deviation
            if core_fit.casefold()=='gaussian':
                fit_mean, fit_std = norm.fit(df['res_'+name][df['res_'+name]>-1][df['res_'+name]<1])
                x = np.linspace(-1,1,200)
                mom_tag = '\n$\mu=$'+str(round(fit_mean,sigfigs=2))+', $\sigma=$'+str(round(fit_std,sigfigs=2)) if include_moments==True else ''
                plt.plot(x,norm.pdf(x,fit_mean,fit_std),label='Gaussian Fit'+mom_tag,color=df.color)
            elif core_fit.casefold()=='cauchy':
                fit_mean, fit_std = cauchy.fit(df['res_'+name][df['res_'+name]>-1][df['res_'+name]<1])
                x = np.linspace(-1,1,200)
                mom_tag = '\n$\mu=$'+str(round(fit_mean,sigfigs=2))+', $\sigma=$'+str(round(fit_std,sigfigs=2)) if include_moments==True else ''
                plt.plot(x,cauchy.pdf(x,fit_mean,fit_std),label='Cauchy Fit'+mom_tag,color=df.color)

        # Add some labels
        plt.legend(prop={'size': 6})
        plt.xlabel(particle.labels_nounits[observable.name]+' '+res)
        plt.ylabel('Normalized Counts')

        # Save figure in save location
        fig_name = res+'_'+dataset.data_type+'_'+name+pt_tag
        plt.savefig(save_loc+fig_name,bbox_inches='tight')
        print('Saved Figure: '+fig_name)

        plt.close()


    def Res_vs_Var(datasets,particle,y_var,x_var,x_bins,save_loc='./',core_fit='nofit'):
        """
        Creates and saves a plot of resolution (or residual) for a given observable against another (or the same) given observable, for all datasets provided, for a given particle.

            Parameters:
                datasets (list of Dataset objects): List of dataset objects of the datasets you want to plot.
                particle (Particle object): Particle object of the particle you want to plot.
                y_var (Observable object): Observable whose resolution (or residuals) will be plotted on the y-axis.
                x_var (Observable object): Observable whose parton level values will be plotted on the x-axis.
                x_bins (list of three floats/ints): x_bins[0] is the bottom edge of the first bin, x_bins[1] is the (max) upper edge of the last bin, and xbins[2] is the width of the bins.

            Options:
                save_loc (str): Directory where you want the histogram saved to (default: current directory).
                core_fit (str): Type of fit you want to use for the width calculations (default: 'nofit', other options: 'gaussian' or 'cauchy').

            Returns:
                Saves histogram in <save_loc> as '<y_var>_<y_res>_vs_<x_var>_<data_type>_<particle>.png'.
        """

        # Get the resolution vs residual specification for the variable on the y-axis
        y_res = y_var.res

        for dataset in datasets:

            # Get dataframe
            df = dataset.df

            # Useful to define
            yfocus = particle.name+'_'+y_var.name

            # Calculate the resolution (or residuals), and wrap phi if that's what we're dealing with
            if y_res.casefold()=='resolution':
                if y_var.name=='phi':
                    df['res_'+yfocus] = Analysis.wrap_phi((df['reco_'+yfocus] - df['truth_'+yfocus]))/df['truth_'+yfocus]
                else:
                    df['res_'+yfocus] = (df['reco_'+yfocus] - df['truth_'+yfocus])/df['truth_'+yfocus]
            else:
                if y_var.name=='phi':
                    df['res_'+yfocus] = Analysis.wrap_phi((df['reco_'+yfocus] - df['truth_'+yfocus]))
                else:
                    df['res_'+yfocus] = df['reco_'+yfocus] - df['truth_'+yfocus]
                
            # Create a scatter plot to be filled
            plt.figure(y_var.name+' '+y_res+' vs '+x_var.name)

            points = []   # Array to hold var vs fwhm values
            for bottom_edge in np.arange(x_bins[0],x_bins[1],x_bins[2]):

                # Set some helpful observables
                top_edge = bottom_edge+x_bins[2]
                middle = bottom_edge+(x_bins[2]/2)

                # Look at resolution at a particular value of var
                cut_temp = df[df['truth_'+particle.name+'_'+x_var.name]>=bottom_edge]      # Should I fold in edges of first and last?
                cut_temp = cut_temp[cut_temp['truth_'+particle.name+'_'+x_var.name]<top_edge]

                # Get standard deviations
                if core_fit=='gaussian':
                    _, sigma = norm.fit(cut_temp['res_'+yfocus][cut_temp['res_'+yfocus]>-1][cut_temp['res_'+yfocus]<1])
                elif core_fit=='cauchy':
                    _, sigma = cauchy.fit(cut_temp['res_'+yfocus][cut_temp['res_'+yfocus]>-1][cut_temp['res_'+yfocus]<1])
                else:
                    sigma = cut_temp['res_'+yfocus].std()
                
                # Add point to list
                points.append([middle,sigma])


            # Set y-axis to a log scale if looking at pt (much higher at low pt)
            if y_var.name=='pt' or y_var.name=='m':
                plt.yscale('log')

            # Put data in the scatterplot
            plt.scatter(np.array(points)[:,0],np.array(points)[:,1],label=dataset.shortname+': '+dataset.cuts+' ('+str(dataset.perc_events)+'%)',color=dataset.color)


        # Add some labels
        plt.xlabel('Parton-level '+particle.labels[x_var.name])
        plt.ylabel('$\sigma$ of '+particle.labels_nounits[y_var.name]+' '+y_res)
        plt.legend(prop={'size': 6})

        # Save figure in save location
        fig_name = y_var.name+'_'+y_res+'_vs_'+x_var.name+'_'+dataset.data_type+'_'+particle.name
        plt.savefig(save_loc+fig_name,bbox_inches='tight')
        print('Saved Figure: '+fig_name)
        
        plt.close()