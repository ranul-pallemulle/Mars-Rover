import unittest
from unittest.mock import patch, Mock
import socket
import select
import coreutils.resource_manager as mgr
from coreutils.resource_manager import Status
from resources.resource import ResourceRawError

class TestResourceManager(unittest.TestCase):
    
    @patch('coreutils.resource_manager.rsc')
    @patch('coreutils.resource_manager.cfg')
    def setUp(self, mocked_cfg, mocked_rsc):
        self.manager = mgr.ResourceManager()
        mocked_cfg.Configuration.ready.return_value = True
        some_names = ["Dolores","Emma","Kathy"]
        mocked_rsc.Resource.get_all_names.return_value = some_names
        some_rsc = Mock()
        some_rsc.policy = mocked_rsc.Policy.UNIQUE
        mocked_rsc.Resource.get.return_value = some_rsc        
        self.manager.initialise()
        self.manager.resources_status["Bertha"] = 0

    @patch('coreutils.resource_manager.rsc')
    @patch('coreutils.resource_manager.cfg')
    def test_initialise(self, mocked_cfg, mocked_rsc):
        mocked_cfg.Configuration.ready.return_value = False
        manager2 = mgr.ResourceManager()        
        with self.assertRaises(mgr.ResourceError):
            manager2.initialise()
        mocked_cfg.Configuration.ready.return_value = True
        mocked_rsc.ResourceRawError = ResourceRawError
        mocked_rsc.Resource.resources_initialise.side_effect = mocked_rsc.ResourceRawError
        with self.assertRaises(mgr.ResourceError):
            manager2.initialise()
        mocked_cfg.Configuration.ready.return_value = True
        mocked_rsc.Resource.resources_initialise.side_effect = None
        some_names = ["Dolores","Emma","Kathy"]
        mocked_rsc.Resource.get_all_names.return_value = some_names
        some_rsc = Mock()
        some_rsc.policy = mocked_rsc.Policy.UNIQUE
        mocked_rsc.Resource.get.return_value = some_rsc
        manager2.initialise()
        self.assertEqual(manager2.resources_status["Dolores"],mgr.Status.FREE)
        self.assertEqual(manager2.resources_status["Emma"],mgr.Status.FREE)
        self.assertEqual(manager2.resources_status["Kathy"],mgr.Status.FREE)
        some_rsc.policy = mocked_rsc.Policy.SHARED
        manager2.initialise()
        self.assertEqual(manager2.resources_status["Dolores"], 0)
        self.assertEqual(manager2.resources_status["Emma"], 0)
        self.assertEqual(manager2.resources_status["Kathy"], 0)

    @patch('coreutils.resource_manager.rsc')
    def test_get_unique(self, mocked_rsc):
        dolores = Mock()
        dolores.policy = mocked_rsc.Policy.UNIQUE
        mocked_rsc.Resource.get.return_value = dolores
        with self.assertRaises(mgr.ResourceError):
            self.manager.get_unique("Somefakeresource")
        self.assertEqual(self.manager.resources_status["Dolores"],mgr.Status.FREE)
        ret = self.manager.get_unique("Dolores")
        self.assertEqual(ret,dolores)
        self.assertEqual(self.manager.resources_status["Dolores"],mgr.Status.ACQUIRED)
        # with self.assertRaises(mgr.ResourceError):
        #     ret = self.manager.get_unique("Dolores")
        ret = self.manager.get_unique('Dolores')
        self.assertIsNone(ret)
        bertha = Mock()
        bertha.policy = mocked_rsc.Policy.SHARED
        mocked_rsc.Resource.get.return_value = bertha
        self.assertEqual(self.manager.resources_status["Bertha"],0)
        with self.assertRaises(mgr.ResourceError):
            ret = self.manager.get_unique("Bertha")

    @patch('coreutils.resource_manager.rsc')
    def test_get_shared(self,mocked_rsc):
        bertha = Mock()
        bertha.policy = mocked_rsc.Policy.SHARED
        mocked_rsc.Resource.get.return_value = bertha        
        self.assertEqual(self.manager.resources_status["Bertha"],0)
        ret = self.manager.get_shared("Bertha")
        self.assertEqual(ret, bertha)
        self.assertEqual(self.manager.resources_status["Bertha"],1)
        bertha.shared_init.assert_called_with()
        for x in range(10):
            ret = self.manager.get_shared("Bertha")
        self.assertEqual(self.manager.resources_status["Bertha"],11)
        dolores = Mock()
        dolores.policy = mocked_rsc.Policy.UNIQUE
        mocked_rsc.Resource.get.return_value = dolores
        with self.assertRaises(mgr.ResourceError):
            ret = self.manager.get_shared("Dolores")

    @patch('coreutils.resource_manager.rsc')
    def test_release(self, mocked_rsc):
        bertha = Mock()
        bertha.policy = mocked_rsc.Policy.SHARED
        mocked_rsc.Resource.get.return_value = bertha
        self.assertEqual(self.manager.resources_status["Bertha"],0)
        ret = self.manager.get_shared("Bertha")
        self.assertEqual(self.manager.resources_status["Bertha"],1)
        bertha.shared_init.assert_called_with()
        ret = self.manager.get_shared("Bertha")
        self.assertEqual(self.manager.resources_status["Bertha"],2)
        self.manager.release("Bertha")
        self.assertEqual(self.manager.resources_status["Bertha"],1)
        self.manager.release("Bertha")
        self.assertEqual(self.manager.resources_status["Bertha"],0)
        bertha.shared_deinit.assert_called_with()
        with self.assertRaises(mgr.ResourceError):
            self.manager.release("Bertha")
        dolores = Mock()
        dolores.policy = mocked_rsc.Policy.UNIQUE
        mocked_rsc.Resource.get.return_value = dolores
        self.assertEqual(self.manager.resources_status["Dolores"],mgr.Status.FREE)
        with self.assertRaises(mgr.ResourceError):
            self.manager.release("Dolores")
        ret = self.manager.get_unique("Dolores")
        self.assertEqual(self.manager.resources_status["Dolores"],mgr.Status.ACQUIRED)
        self.manager.release("Dolores")
        self.assertEqual(self.manager.resources_status["Dolores"],mgr.Status.FREE)
              
