# README #

This README gives a broad overview on the procedures required to reproduce
the results described in my master's thesis:

    Michael Haas: "Weakly Supervised Learning for Compositional Sentiment
    Recognition in German", 2014. Supervised by Dr. Yannick Versley

# Setup #

The experiments and supporting software are mainly written in Bash,
Python 2 and Java.


## Bash Setup ##

The bash scripts require that you set the location of the code and the data
directories. Open *scripts/common.sh* in your favorite editor and set the
paths. An example:

    DATADIR="$HOME/ma/"
    CODEDIR="$HOME/kurse/Master-Arbeit/code/"

$CODEDIR refers to the package containing this README file.

## Python Setup ##

I recommend that you set up a virtualenv to install the dependencies to ensure
that you start from a clean slate. The list of required python software along
with the exact version specification is noted in requirements.txt.

If you do not have the virtualenv package, install it from your distribution's
package repository:

    # For Debian and Ubuntu
    apt-get install python-virtualenv

Or use a package manager for Python such as pip to install it to your home
directory:

    pip install --user virtualenv
    # You might want to add this to .~/bashrc
    export PATH=$PATH:$HOME/.local/bin/

Then create a new and active a new virtualenv:

    virtualenv $HOME/haas-thesis-env/
    source $HOME/haas-thesis-env/bin/activate

From this clean slate, install the required dependencies.

    pip install nltk==2.0.4
    pip install numpy
    pip install -r requirements.txt

NLTK is installed separately to work around somewhat lackluster
dependency declaration by the packages listed in requirements.txt.


## Java Setup ##

To compile the java code, run the *build.sh* script:

    source scripts/common.sh
    cd MA/
    bash build.sh

Note that this script also extracts the Stanford CoreNLP
package located in $DATADIR/3rdparty/.


## GNÚ Parallel Setup ##


The scripts which run the experiments depend on GNU parallel.
I recommend you install version 20140822 or newer. Either get it from
your package manager or from [GNU](https://www.gnu.org/software/parallel/).
Please make sure your version is not too old.

GNU parallel greatly speeds up training by distributing tasks across multiple
CPUs or even across multiple nodes on a cluster. If you have multiple compute
nodes, you will need to set up password-less SSH logins. Refer to the
documentation on
['Using Remote Computers'](https://www.gnu.org/software/parallel/man.html#EXAMPLE:-Using-remote-computers).
Then edit scripts/common/run_train_common.sh and add your compute nodes to the
HOST variable like this:

    HOSTS="ella,10.0.0.2"

The experiments expect that the data is available on every node in the same
location. This is a typical setup for computer labels where home directories
are stored on a central server and exported via NFS to the workstations. If
you do not have such a setup, consider using the --transfer flag for parallel.

Finally, if you do not want to use remote compute nodes, just tell parallel
to only use the local host:

    HOSTS=":"


# Run the experiments #

To run all experiments, execute thesis\_run\_ALL\_experiments.sh:

    cd scripts/
    bash thesis_run_ALL_experiments.sh

To run individual experiments, look at all files starting with thesis\_run:

    ls scripts/thesis_run*sh

The results will be located in the data directory, one subdirectory per
experiment. A file *all.csv* or *all-combined.csv* will reside in each
subdirectory. There, you can find the node F1 and root accuracy measures
in the *combinedLabelFMacro* and *combinedRootLabelAccMacro* columns.
*all.csv* contains the results of all splits in a ten-fold cross-validation
experiments. The last row contains the averages across all splits, which is
what is reported in my thesis and in *all-combined.csv*.
Files named  *contrastive_conjunctions.csv* contain the results of the
contrastive conjunctions task. Likewise,
*accuracy_at_length.csv* is the file name for the accuracy at length measures.
*evaluate_productions.txt* is the file name for the rule-base task.

If you'd like to re-create the HeiST-592 data set from annotations and parse trees,
run:

    cd scripts/
    bash thesis_crowdflower_to_tree.sh

# Directory Listing #

* MA/: Java code. Contains various tree handling routines and contrastive
  conjunctions test.
* cf/: Code relating to CrowdFlower
* german\_movie\_reviews/: Crawling and processing for film-rezensionen.de reviews
* google\_translate/: Interface to Google Translate, required for Projection
* ml/: Various machine-learning tools, e.g. Ensemble 
* projection:/ Projection of sentiment labels for parse trees 
* requirements.txt: List of dependencies
* scripts/: Support scripts and main experiments
* sentiws/: Naive sentiment analysis using sentiment lexicons

