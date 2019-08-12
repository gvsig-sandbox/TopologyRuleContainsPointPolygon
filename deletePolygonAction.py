# encoding: utf-8

import gvsig
import sys

from org.gvsig.topology.lib.spi import AbstractTopologyRuleAction

class DeletePolygonAction(AbstractTopologyRuleAction):
    
    def __init__(self):
        AbstractTopologyRuleAction.__init__(
            self,
	    "containsPointPolygon",
            "DeletePolygonAction",
            "Delete Polygon Action",
            " Polygons that not contains at least one point from the points layer must be deleted. The delete action removes polygon entities that not contains points."
        )
    
    def execute(self, rule, line, parameters):
	#TopologyRule rule, TopologyReportLine line, DynObject parameters) {
        try:
            dataSet = rule.getDataSet1()
            dataSet.delete(line.getFeature1())
        except:
            ex = sys.exc_info()[1]
            gvsig.logger("Can't execute action. Class Name: " + ex.__class__.__name__ + ". Exception: " + str(ex), gvsig.LOGGER_ERROR)

def main(*args):
    pass
