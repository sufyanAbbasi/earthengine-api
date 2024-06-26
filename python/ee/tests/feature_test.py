#!/usr/bin/env python3
"""Test for the ee.feature module."""

import ee
from ee import apitestcase
import unittest


class FeatureTest(apitestcase.ApiTestCase):

  def testConstructors(self):
    """Verifies that constructors understand valid parameters."""
    point = ee.Geometry.Point(1, 2)
    from_geometry = ee.Feature(point)
    self.assertEqual(ee.ApiFunction('Feature'), from_geometry.func)
    self.assertEqual({'geometry': point, 'metadata': None}, from_geometry.args)

    from_null_geometry = ee.Feature(None, {'x': 2})
    self.assertEqual(ee.ApiFunction('Feature'), from_null_geometry.func)
    self.assertEqual({
        'geometry': None,
        'metadata': {
            'x': 2
        }
    }, from_null_geometry.args)

    computed_geometry = ee.Geometry(ee.ComputedObject(ee.Function(), {'a': 1}))
    computed_properties = ee.ComputedObject(ee.Function(), {'b': 2})
    from_computed_one = ee.Feature(computed_geometry)
    from_computed_both = ee.Feature(computed_geometry, computed_properties)
    self.assertEqual(ee.ApiFunction('Feature'), from_computed_one.func)
    self.assertEqual({
        'geometry': computed_geometry,
        'metadata': None
    }, from_computed_one.args)
    self.assertEqual(ee.ApiFunction('Feature'), from_computed_both.func)
    self.assertEqual({
        'geometry': computed_geometry,
        'metadata': computed_properties
    }, from_computed_both.args)

    from_variable = ee.Feature(ee.CustomFunction.variable(None, 'foo'))
    self.assertIsInstance(from_variable, ee.Feature)

    result = from_variable.encode(None)
    self.assertEqual({'type': 'ArgumentRef', 'value': 'foo'}, result)

    from_geo_json_feature = ee.Feature({
        'type': 'Feature',
        'id': 'bar',
        'geometry': point.toGeoJSON(),
        'properties': {'foo': 42}
    })
    self.assertEqual(ee.ApiFunction('Feature'), from_geo_json_feature.func)
    self.assertEqual(point, from_geo_json_feature.args['geometry'])
    self.assertEqual({
        'foo': 42,
        'system:index': 'bar'
    }, from_geo_json_feature.args['metadata'])

  def testGetMap(self):
    """Verifies that getMap() uses Collection.draw to rasterize Features."""
    feature = ee.Feature(None)
    mapid = feature.getMapId({'color': 'ABCDEF'})
    manual = ee.ApiFunction.apply_('Collection.draw', {
        'collection': ee.FeatureCollection([feature]),
        'color': 'ABCDEF'})

    self.assertEqual('fakeMapId', mapid['mapid'])
    self.assertEqual(manual.serialize(), mapid['image'].serialize())

  def testInitOptParams(self):
    result = ee.Feature(
        geom=ee.Geometry.Point(1, 2), opt_properties=dict(prop='a')
    ).serialize()
    self.assertIn('"metadata": {"constantValue": {"prop": "a"}}', result)


if __name__ == '__main__':
  unittest.main()
