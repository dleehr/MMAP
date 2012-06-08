"""
Created on Mar 20, 2012

@author: Erin McKenney
"""

import unittest
import os
from core.component.run_MetaSim import RunMetaSim
from core import run_ext_prog
from core.utils import path_utils

class TestRunMetaSim(unittest.TestCase):

    platform = run_ext_prog.get_platform()

    def setUp(self):
        self.long_message = True
        self.data_dir = path_utils.get_data_dir() + "MetaSim/"
        self.working_dir = path_utils.get_data_dir() + "MetaSim/test_data/"

    def tearDown(self):
        pass

    # Parameters to check: model_infile, no_reads, taxon_infile, pdir, wdir=None, outfile=None
        # MODEL_INFILE_POSITION = 1
        #NO_READS_POSITION = 2
        #TAXON_INFILE_POSITION = 3
        #OUTFILE_DIRECTORY_POSITION = 4

    def test_RunMetaSim_init(self):
        model_infile_var = "ErrorModelSolexa36bp.mconf"
        taxon_infile_var = "MetaSim_bint.mprf"
        outfile_var = "wdir_all_reads_out.fasta"
        no_reads_var = 100

        metasim = RunMetaSim(model_file=model_infile_var, no_reads=no_reads_var,
            taxon_infile =taxon_infile_var, pdir=self.data_dir, wdir=self.working_dir,
            outfile=outfile_var, check_exist=True)

        expected_model_infile = "-mg %s%s"%(self.working_dir, model_infile_var)
        expected_taxon_infile = self.working_dir + taxon_infile_var
        expected_no_reads = "-r%s" % no_reads_var
        expected_outfile = "-d %s"%self.working_dir + "wdir_all_reads_out.fasta"
        expected = [expected_model_infile, expected_no_reads, expected_taxon_infile, expected_outfile]
#
        self.assertEqual(metasim.get_switch()[0], "-mg %s%s"%(self.working_dir, model_infile_var))
        self.assertEqual(metasim.get_switch()[1], expected_no_reads)
        self.assertEqual(metasim.get_switch()[2], expected_taxon_infile)
        self.assertEqual(metasim.get_switch()[3], expected_outfile)
        self.assertEqual(metasim.get_switch(), [expected_model_infile, expected_no_reads,expected_taxon_infile,expected_outfile])
        self.assertEqual(metasim.get_switch(), expected)

    def test_file_not_exist(self):
        model_infile_var = "file_inexistent.mconf"  # test model_infile
        taxon_infile_var = "MetaSim_bint.mprf"
        outfile_var = "wdir_all_reads_out.fasta"
        no_reads_var = 100

        with self.assertRaises(IOError):
            RunMetaSim(model_file=model_infile_var, no_reads=no_reads_var,
            taxon_infile =taxon_infile_var, pdir=self.data_dir, wdir=self.working_dir,
            outfile=outfile_var, check_exist=True)

        model_infile_var = "ErrorModelSolexa36bp.mconf"
        taxon_infile_var = "bad_file.mprf"          # test taxon_infile

        with self.assertRaises(IOError):
            RunMetaSim(model_file=model_infile_var, no_reads=no_reads_var,
                taxon_infile =taxon_infile_var, pdir=self.data_dir, wdir=self.working_dir,
                outfile=outfile_var, check_exist=True)

        taxon_infile_var = "MetaSim_bint.mprf"
        outfile_var = "incorrect_outfile.fasta"     # test outfile

        with self.assertRaises(IOError):
            RunMetaSim(model_file=model_infile_var, no_reads=no_reads_var,
                taxon_infile =taxon_infile_var, pdir=self.data_dir, wdir=self.working_dir,
                outfile=outfile_var, check_exist=True)

    def test_no_reads_value(self):
        model_infile_var = "ErrorModelSolexa36bp.mconf"
        taxon_infile_var = "MetaSim_bint.mprf"
        outfile_var = "wdir_all_reads_out.fasta"

        metasim = RunMetaSim(model_file=model_infile_var, no_reads=100,
            taxon_infile =taxon_infile_var, pdir=self.data_dir, wdir=self.working_dir,
            outfile=outfile_var, check_exist=True)
        self.assertRaises(ValueError, metasim.set_number_of_reads, 1.1)
        self.assertRaises(ValueError, metasim.set_number_of_reads, -1)
        self.assertRaises(ValueError, metasim.set_number_of_reads, -2.5)
        self.assertRaises(TypeError, metasim.set_number_of_reads, "string")
        self.assertRaises(TypeError, metasim.set_number_of_reads, "3")

    def test_set_outfile_directory(self):
        model_infile_var = "ErrorModelSolexa36bp.mconf"
        taxon_infile_var = "MetaSim_bint.mprf"
        outfile_var = "wdir_all_reads_out.fasta"

        metasim = RunMetaSim(model_file=model_infile_var, no_reads=100,
            taxon_infile =taxon_infile_var, pdir=self.data_dir, wdir=self.working_dir,
            outfile=outfile_var, check_exist=True)

        self.assertEqual(metasim.get_switch()[3], "-d %swdir_all_reads_out.fasta"%self.working_dir)

        outfile_var = "new_outfile.fasta"
        metasim = RunMetaSim(model_file=model_infile_var, no_reads=100,
            taxon_infile =taxon_infile_var, pdir=self.data_dir, wdir=self.working_dir,
            outfile=outfile_var, check_exist=True)
        metasim.set_outfile_directory()
        self.assertEqual(metasim.get_switch()[3], "-d %snew_outfile.fasta"%self.working_dir)

    def test_file_already_exist(self):
        """
        check if out file already exists,
        maybe should not raise error, should
        TODO: maybe it should be handle it at different way, auto rename?
        """
        model_infile_var = "ErrorModelSolexa36bp.mconf"
        taxon_infile_var = "MetaSim_bint.mprf"
        outfile_var = self.working_dir + "testOutFileAlreadyExist.fasta"
        with self.assertRaises(IOError):
            RunMetaSim(model_file=model_infile_var, no_reads=100,
                taxon_infile =taxon_infile_var, pdir=self.data_dir, wdir=self.working_dir,
                outfile=outfile_var, check_exist=True)

    def test_check_outfile_exist(self):
        """
        check if ./MetaSim finished running, should produce 2 output files
        only pass if both exist
        """
        model_infile_var = "ErrorModelSolexa36bp.mconf"
        taxon_infile_var = "MetaSim_bint.mprf"
        outfile_var = "MetaSim_bint-454.20e39f4c.fna"

        metasim = RunMetaSim(model_file=model_infile_var, no_reads=100,
            taxon_infile =taxon_infile_var, pdir=self.data_dir, wdir=self.working_dir,
            outfile=outfile_var, check_exist=True)
        print self.working_dir
        print metasim.outfile
        self.assertTrue(metasim.check_outfiles_exist(self.working_dir + "%sMetaSim_bint-454.20e39f4c.fna"))


        # negative test, outfiles are not suppose to exist
        outfile_var = "fileNotExist.fasta"
        with self.assertRaises(IOError):
            RunMetaSim(model_file=model_infile_var, no_reads=100,
                taxon_infile =taxon_infile_var, pdir=self.data_dir, wdir=self.working_dir,
                outfile=outfile_var, check_exist=True)