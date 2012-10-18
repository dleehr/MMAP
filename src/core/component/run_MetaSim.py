"""
Created on May 30, 2012
@author: Erin McKenney
"""
from Bio import SeqIO
import os
from core.component.run_component import RunComponent
from core.run_ext_prog import runExtProg

# Full command-line sequence will read as
# ./MetaSim cmd -mg /path.mconf -r### /path.mprf -d /path/output_directory
# <run MetaSim in command mode>
# <use empirical model with specified config file --> alternately, -4 --454 error model>
# <generate ### reads>
# <using specified taxon file or single genome seq in FASTA format>
# <specify output directory>

#TOREAD(Erin): cmd has to be the very first switch, 
METASIM = "./MetaSim" # .MetaSim cmd
MODEL_INFILE_POSITION = 2
NO_READS_POSITION = 3
OUTFILE_DIRECTORY_POSITION = 4
TAXON_INFILE_POSITION = 5


ALL_EXTS = [".fna"]

class RunMetaSim(RunComponent):
    """
    classdocs
    
    run with
    ./MetaSim cmd -f 100 -r 10 -c -d test_data test_data/test_infile.fasta
    ./MetaSim cmd --454 -f 200 --454-cycles 99 --454-mate-probability 0 -r20 -c -d outfile_dir infile_name
    """

    def __init__(self, model_file, no_reads, taxon_infile, pdir, wdir, outfile=None, check_exist=True):
        """
        Constructor
        """

        self.all_exts = ALL_EXTS
        self.parameter_check(pdir, wdir, model_file, taxon_infile, outfile, check_exist)
        self.metasim = runExtProg(METASIM, pdir=self.pdir, length=5, check_OS=True)
        self.metasim.set_param_at("cmd", 1)
        self.init_prog(no_reads)


    @classmethod
    def create_metasim(cls, setting):
        """
        Class method
        Create RunGlimmer from dict()
        """
        metasim = cls(model_file=setting.get("metasim_model_infile"),
            no_reads=setting.get("metasim_no_reads"),
            taxon_infile=setting.get("metasim_taxon_infile"),
            pdir=setting.get("metasim_pdir"),
            wdir=setting.get("wdir"),
            outfile=setting.get("metasim_outfile"),
            check_exist=setting.get("check_exist"))
        return metasim

    @classmethod
    def create_metasim_from_setting(cls, setting_class):
        """
        Class method
        Create RunGlimmer from Setting class
        """
        setting = setting_class.get_all_par("metasim")
        metasim = RunMetaSim.create_metasim(setting)
        return metasim

    def parameter_check(self, pdir, wdir, model_file, taxon_infile, outfile, check_exist):
        #TODO: check outdir exist
        self.check_dirs(pdir, wdir, check_exist)
        self.generate_outfile_name(taxon_infile, outfile, error_model="-454" or "-Sanger" or "-Empirical")
        self.model_infile = self.wdir + model_file
        self.taxon_infile = self.wdir + taxon_infile
#        print "SELF.WDIR",self.wdir, "OUTFILE",outfile
#        self.outfile = self.wdir + outfile
        files = [self.model_infile, self.taxon_infile]
        for file in files:
            self.check_file_exist(file, check_exist)
#            self.model_infile, self.taxon_infile, self.outfile)


    def init_prog(self, no_reads):
        self.set_model_infile_name()
        self.set_taxon_infile_name()
        self.set_number_of_reads(no_reads)
        self.set_outfile_directory()


    def set_number_of_reads(self, param):
        if param > 0 and isinstance(param, (int, long)):
            arg = "-r%s" % param
            self.metasim.set_param_at(arg, NO_READS_POSITION)
        else:
            if isinstance(param, str):
                raise TypeError("Error: number of reads set as string: %s" % param)
            else:
                raise ValueError("Error: number of reads set to: %s" % param)

#        TODO: if NONE, set to default # of reads
#        in setting.py or __init__ (as with check_exist)?


    def set_model_infile_name(self):
        """
        type anything here
        TODO: check valid infile, infile exist or not
        """

        arg = "-mg%s" % self.model_infile
        self.metasim.set_param_at(arg, MODEL_INFILE_POSITION)


    def set_taxon_infile_name(self):
        """
        type anything here
        TODO: check valid infile, infile exist or not
        """

        self.metasim.set_param_at(self.taxon_infile, TAXON_INFILE_POSITION)

    def set_outfile_directory(self):
        directory = "-d%s" % self.wdir
        self.metasim.set_param_at(directory, OUTFILE_DIRECTORY_POSITION)

    def generate_outfile_name(self, infile, outfile, error_model):
        """
        infile name
            check if it exist
            if yes, append <namebase>.#
        if os.path.exists(  self.cwd+self.name_only  ):
        if os.path.exists(  full_file_path  ):
        """
        self.infile = self.wdir + infile
        location = infile.rfind(".")
        if location is -1:
            namebase = infile
        else:
            namebase = infile[0:location]
            #            print "qq", self.wdir ,namebase , outfile_tag
        self.outfile = self.wdir + namebase
#        now append model type
        if error_model=="-454" or "-Sanger" or "-Empirical":
            self.outfile = self.wdir + namebase + error_model
        else:
            raise TypeError("Error: invalid error model: %s" %error_model)
#        now self.outfile = /dir/namebase-Model
#        if doesn't exist, append
        if not os.path.exists(self.outfile+".fna"):
            self.outfile = self.wdir + namebase + error_model + ".fna"
        else:
            version = 1
            while os.path.exists(self.wdir + namebase + error_model + ".%.fna" %version):
                version = version + 1
            self.outfile = self.wdir + namebase + error_model + ".%.fna" %version
            print "?????????????",self.outfile


    def read_outfile(self):
        """
        use SeqIO.index(file, "fast") to read the result seq file,
        generated from ./finalize
        TODO: check outfile exist, properly generated by ./finalize
        """
        print "!!!!!!!!!!!!",self.outfile
        self.record_index = SeqIO.index(self.outfile, "fasta")
        return self.record_index

    def run(self, debug=False):
        self.metasim.run(debug)

    def get_switch(self):
        return self.metasim._switch
