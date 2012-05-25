"""
Created on Feb 29, 2012

@author: Erin McKenney and Steven Wu
"""
from Bio import SeqIO
from core.component.run_component import RunComponent
from core.run_ext_prog import runExtProg

ASSEMBLE = "./assemble"
ASSEMBLE_NO_ITER_POSITION = 2
ASSEMBLE_INFILE_POSITION = 1

FINALIZE = "./finalize"
FINALIZE_CUTOFF_POSITION = 1
FINALIZE_OUTFILE_POSITION = 2
FINALIZE_INFILE_POSITION = 3

ALL_EXTS = [".status", ".dump1", ".dump.best"]


class RunGenovo(RunComponent):
    """
    classdocs

    """

    def __init__(self, infile, no_iter, thresh, pdir, wdir=None,
                 outfile=None, check_exist=True):
        """
        Constructor
        TODO: implement finalize
        TODO: read/parse/check output
        #        super(RunGenovo, self).__init__()
        """
        self.all_exts = ALL_EXTS
        self.parameter_check(pdir, wdir, infile, outfile, check_exist, "_out.fasta")

        self.assemble = runExtProg(ASSEMBLE, pdir=self.pdir, length=2, check_OS=True)
        self.finalize = runExtProg(FINALIZE, pdir=self.pdir, length=3, check_OS=True)

        self.init_prog(no_iter, thresh)

    @classmethod
    def create_genovo(cls, setting):
        genovo = cls(infile=setting.get("genovo_infile"),
                     no_iter=setting.get("genovo_noI"),
                     thresh=setting.get("genovo_thresh"),
                     pdir=setting.get("genovo_pdir"),
                     wdir=setting.get("wdir"),
                     outfile=setting.get("genovo_outfile"),
                     check_exist=setting.get("check_exist"))
        return genovo

    @classmethod
    def create_genovo_from_setting(cls, setting_class):
        setting = setting_class.get_all_par("genovo")
        genovo = RunGenovo.create_genovo(setting)
        return genovo

    def init_prog(self, no_iter, thresh):
        self.set_infile_name(self.infile)
        self.set_outfile(self.outfile)
        self.set_number_of_iter(no_iter)
        self.set_cutoff(thresh)

    def set_number_of_iter(self, param):
        if param > 0 and isinstance(param, (int, long)):
            self.assemble.set_param_at(param, ASSEMBLE_NO_ITER_POSITION)
        else:
            raise TypeError("Error: unacceptable value for param: %s" % param)

    def set_infile_name(self, infile):
        """
        type anything here
        TODO: check valid infile, infile exist or not
        """
        self.assemble.set_param_at(infile, ASSEMBLE_INFILE_POSITION)
        self.finalize.set_param_at(infile + ".dump.best",
                                   FINALIZE_INFILE_POSITION)

    def set_outfile(self, outfile):
        self.finalize.set_param_at(outfile, FINALIZE_OUTFILE_POSITION)

    def set_cutoff(self, v):
        if v > 0 and isinstance(v, (int, long)):
            self.finalize.set_param_at(v, FINALIZE_CUTOFF_POSITION)
        else:
            if isinstance(v, str):
                raise TypeError('Error: cutoff set as string "%s"' % v)
            else:
                raise ValueError('Error: cutoff set to:', v)

    def read_outfile(self):
        """
        use SeqIO.index(file, "fast") to read the result seq file,
        generated from ./finalize
        TODO: check outfile exist, properly generated by ./finalize
        """
        self.record_index = SeqIO.index(self.outfile, "fasta")
        return self.record_index

    def run(self):
        self.assemble.run()
        self.finalize.run()

