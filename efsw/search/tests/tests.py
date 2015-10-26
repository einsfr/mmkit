import os
import datetime

from django.db import connection
from django.test import TestCase
from django.conf import settings

from efsw.search import elastic
from efsw.search.management.commands import esinit
from efsw.search.tests import models as test_models


class SearchTestCase(TestCase):

    def testConnection(self):
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            es = elastic.get_connection_manager().get_es()
            another_es = elastic.get_connection_manager().get_es()
        self.assertTrue(es is another_es)

    def testInitialization(self):
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            es = elastic.get_connection_manager().get_es()
        cmd = esinit.Command()
        base_dir = getattr(settings, 'BASE_DIR')
        init_indices = (
            os.path.join(base_dir, 'non-existent-file.json'),
        )
        with self.settings(
                EFSW_ELASTIC_INIT_INDICES=init_indices,
                EFSW_ELASTIC_DISABLE=False
        ):
            with self.assertRaises(FileNotFoundError):
                cmd.handle(replace=True, verbosity=2, nowait=False)

        init_indices = (
            os.path.join(base_dir, 'efsw', 'search', 'tests', 'testindex.json'),
            os.path.join(base_dir, 'efsw', 'search', 'tests', 'indices'),
        )
        with self.settings(
                EFSW_ELASTIC_INIT_INDICES=init_indices,
                EFSW_ELASTIC_DISABLE=False
        ):
            cmd.handle(replace=True, verbosity=2, nowait=False)
        index_prefix = elastic.get_connection_manager().get_es_index_prefix()
        reply = es.indices.get(index='{0}testindex'.format(index_prefix), feature='_mappings')
        self.assertEqual(reply, {
            '{0}testindex'.format(index_prefix): {
                'mappings': {'testmapping': {'properties': {'testproperty': {'type': 'string'}}}}
            }
        })

        reply = es.indices.get(index='{0}andanotherone'.format(index_prefix), feature='_mappings')
        self.assertEqual(reply, {
            '{0}andanotherone'.format(index_prefix): {
                'mappings': {'andanothermapping': {'properties': {'testproperty': {'type': 'string'}}}}
            }
        })

        reply = es.indices.get(index='{0}anotherindex'.format(index_prefix), feature='_mappings')
        self.assertEqual(reply, {
            '{0}anotherindex'.format(index_prefix): {
                'mappings': {'anothermapping': {'properties': {'testproperty': {'type': 'string'}}}}
            }
        })


class ModelIndexTestCase(TestCase):

    def testModelCreation(self):
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            es = elastic.get_connection_manager().get_es()
        init_indices = (
            os.path.join(getattr(settings, 'BASE_DIR'), 'efsw', 'search', 'tests', 'testmodelindex.json'),
            os.path.join(getattr(settings, 'BASE_DIR'), 'efsw', 'search', 'tests', 'sourcelessindex.json'),
        )
        with self.settings(
                EFSW_ELASTIC_INIT_INDICES=init_indices,
                EFSW_ELASTIC_DISABLE=False
        ):
            esinit.Command().handle(replace=True, verbosity=2, nowait=False)
        m = test_models.IndexableTestModel()
        sm = test_models.SourcelessIndexableTestModel()
        m.name = sm.name = 'Test Model 1'
        m.created = sm.created = datetime.date.today()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(m)
            schema_editor.create_model(sm)
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            m.save()
            sm.save()
        reply = es.get(elastic.get_connection_manager().prefix_index_name('testmodelindex'), m.id, 'indexabletestmodel')
        self.assertEqual(reply['_index'], elastic.get_connection_manager().prefix_index_name('testmodelindex'))
        self.assertEqual(reply['_source']['created'], m.created.isoformat())
        self.assertEqual(reply['_source']['name'], m.name)
        self.assertEqual(reply['_type'], 'indexabletestmodel')
        self.assertEqual(reply['_id'], str(m.id))
        self.assertTrue(reply['found'])
        reply = es.get(
            elastic.get_connection_manager().prefix_index_name('sourcelessindex'), sm.id,
            'sourcelessindexabletestmodel')
        self.assertTrue(reply['found'])
        self.assertNotIn('_source', reply)
        m.name = sm.name = 'Edited Test Model 1'
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            m.save()
            sm.save()
        reply = es.get(elastic.get_connection_manager().prefix_index_name('testmodelindex'), m.id, 'indexabletestmodel')
        self.assertEqual(reply['_index'], elastic.get_connection_manager().prefix_index_name('testmodelindex'))
        self.assertEqual(reply['_source']['created'], m.created.isoformat())
        self.assertEqual(reply['_source']['name'], m.name)
        self.assertEqual(reply['_type'], 'indexabletestmodel')
        self.assertEqual(reply['_id'], str(m.id))
        self.assertTrue(reply['found'])
        reply = es.get(
            elastic.get_connection_manager().prefix_index_name('sourcelessindex'), sm.id,
            'sourcelessindexabletestmodel')
        self.assertTrue(reply['found'])
        self.assertNotIn('_source', reply)
        model_id = m.id
        smodel_id = sm.id
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            m.delete()
            sm.delete()
        reply = es.get(
            elastic.get_connection_manager().prefix_index_name('testmodelindex'), model_id, 'indexabletestmodel',
            ignore=404)
        self.assertFalse(reply['found'])
        reply = es.get(
            elastic.get_connection_manager().prefix_index_name('sourcelessindex'), smodel_id,
            'sourcelessindexabletestmodel', ignore=404)
        self.assertFalse(reply['found'])
