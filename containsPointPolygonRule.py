# encoding: utf-8

import gvsig
import sys

from gvsig import geom
from gvsig import uselib
uselib.use_plugin("org.gvsig.topology.app.mainplugin")

from org.gvsig.expressionevaluator import ExpressionEvaluatorLocator
from org.gvsig.topology.lib.api import TopologyLocator
from org.gvsig.topology.lib.spi import AbstractTopologyRule

from deletePointAction import DeletePointAction

class ContainsPointPolygonRule(AbstractTopologyRule):
    
    geomName = None
    expression = None
    expressionBuilder = None
    
    def __init__(self, plan, factory, tolerance, dataSet1, dataSet2):
        AbstractTopologyRule.__init__(self, plan, factory, tolerance, dataSet1, dataSet2)
        self.addAction(DeletePointAction())
    
    def intersects(self, polygon1, theDataSet2):
        if theDataSet2.getSpatialIndex() != None:
            result = False
            for featureReference in theDataSet2.query(polygon1):
                feature2 = featureReference.getFeature()
                point2 = feature2.getDefaultGeometry()
                if polygon1.intersects(point2):
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
                    self.expressionBuilder.ST_Intersects(
                        self.expressionBuilder.geometry(polygon1),
                        self.expressionBuilder.column(self.geomName)
                    )
                ).toString()
            )
            if theDataSet2.findFirst(self.expression) == None:
                result = False
            else:
                result = True
        return result
    
    def check(self, taskStatus, report, feature1):
        try:
            polygon1 = feature1.getDefaultGeometry()
            tolerance1 = self.getTolerance()
            theDataSet2 = self.getDataSet2()
            geometryType1 = polygon1.getGeometryType()
            if geometryType1.getSubType() == geom.D2 or geometryType1.getSubType() == geom.D2M:
                if geometryType1.getType() == geom.SURFACE:
                    if not self.intersects(polygon1, theDataSet2):
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
                            "Geometry Type: Polygon not contains point",
                            ""
                        )
                else:
                    if geometryType1.getType() == geom.MULTISURFACE:
                        n1 = polygon1.getPrimitivesNumber()
                        for i in range(0, n1 + 1):
                            if not self.intersects(polygon1, theDataSet2):
                                report.addLine(self,
                                    self.getDataSet1(),
                                    self.getDataSet2(),
                                    polygon1,
                                    polygon1.getPointAt(i),
                                    feature1.getReference(), 
                                    None,
                                    i,
                                    -1,
                                    False,
                                    "Geometry Type multiPolygon not contains point",
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
