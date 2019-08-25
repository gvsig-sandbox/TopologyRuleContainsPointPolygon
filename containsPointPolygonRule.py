# encoding: utf-8

import gvsig
import sys

from gvsig import geom
from gvsig import uselib
uselib.use_plugin("org.gvsig.topology.app.mainplugin")

from org.gvsig.expressionevaluator import ExpressionEvaluatorLocator
from org.gvsig.topology.lib.api import TopologyLocator
from org.gvsig.topology.lib.spi import AbstractTopologyRule

from deletePolygonAction import DeletePolygonAction

class ContainsPointPolygonRule(AbstractTopologyRule):
    
    geomName = None
    expression = None
    expressionBuilder = None
    
    def __init__(self, plan, factory, tolerance, dataSet1, dataSet2):
        AbstractTopologyRule.__init__(self, plan, factory, tolerance, dataSet1, dataSet2)
        self.addAction(DeletePolygonAction())
    
    def contains(self, polygon1, theDataSet2):
        result = False
        if theDataSet2.getSpatialIndex() != None:
            for featureReference in theDataSet2.query(polygon1):
                feature2 = featureReference.getFeature()
                point2 = feature2.getDefaultGeometry()
                if polygon1.contains(point2):
                    result = True
                    break
        else:
            if self.expression == None:
                manager = ExpressionEvaluatorLocator.getManager()
                self.expression = manager.createExpression()
                self.expressionBuilder = manager.createExpressionBuilder()
                store2 = theDataSet2.getFeatureStore()
                self.geomName = store2.getDefaultFeatureType().getDefaultGeometryAttributeName()
            self.expression.setPhrase(
                self.expressionBuilder.ifnull(
                    self.expressionBuilder.column(self.geomName),
                    self.expressionBuilder.constant(False),
                    self.expressionBuilder.ST_Contains(
                        self.expressionBuilder.geometry(polygon1),
                        self.expressionBuilder.column(self.geomName)
                    )
                ).toString()
            )
            if theDataSet2.findFirst(self.expression) != None:
                result = True
        return result
    
    def check(self, taskStatus, report, feature1):
        try:
            polygon1 = feature1.getDefaultGeometry()
            theDataSet2 = self.getDataSet2()
            geometryType1 = polygon1.getGeometryType()
            if geometryType1.getSubType() == geom.D2 or geometryType1.getSubType() == geom.D2M:
                if geometryType1.getType() == geom.POLYGON or geometryType1.isTypeOf(geom.POLYGON):
                    if not self.contains(polygon1, theDataSet2):
                        report.addLine(self,
                            self.getDataSet1(),
                            self.getDataSet2(),
                            polygon1,
                            polygon1,
                            feature1.getReference(),
                            None,
                            -1,
                            -1,
                            False,
                            "Geometry type polygon doesn't contain points.",
                            ""
                        )
                else:
                    if geometryType1.getType() == geom.MULTIPOLYGON or geometryType1.isTypeOf(geom.MULTIPOLYGON):
                        n1 = point1.getPrimitivesNumber()
                        for i in range(0, n1 + 1):
                            if not self.contains(polygon1.getSurfaceAt(i), theDataSet2):
                                report.addLine(self,
                                    self.getDataSet1(),
                                    self.getDataSet2(),
                                    polygon1,
                                    polygon1.getSurfaceAt(i),
                                    feature1.getReference(), 
                                    None,
                                    i,
                                    -1,
                                    False,
                                    "Geometry type multipolygon doesn't contain points.",
                                    ""
                                )
            else:
                report.addLine(self,
                    self.getDataSet1(),
                    self.getDataSet2(),
                    polygon1,
                    polygon1,
                    feature1.getReference(),
                    None,
                    -1,
                    -1,
                    False,
                    "Unsupported geometry subtype.",
                    ""
                )
        except:
            ex = sys.exc_info()[1]
            gvsig.logger("Can't execute rule. Class Name: " + ex.__class__.__name__ + ". Exception: " + str(ex), gvsig.LOGGER_ERROR)

def main(*args):
    pass