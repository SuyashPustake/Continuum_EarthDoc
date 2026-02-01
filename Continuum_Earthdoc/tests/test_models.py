"""
Comprehensive tests for models: project, methodology, evidence.
"""

import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestProjectModels(unittest.TestCase):
    """Tests for models.project."""

    def test_project_info(self):
        from models.project import ProjectInfo
        info = ProjectInfo(
            project_title="Test",
            proponent_name="Acme",
            proponent_contact="a@b.com",
            country="US",
            project_area_hectares=100.0,
            project_start_date=date(2025, 1, 1),
            crediting_period_start=date(2025, 1, 1),
            crediting_period_end=date(2032, 1, 1),
            crediting_period_years=7,
        )
        self.assertEqual(info.project_title, "Test")
        self.assertEqual(info.country, "US")
        self.assertEqual(info.methodology_id, "VM0042")

    def test_project_data(self):
        from models.project import ProjectData
        data = ProjectData(
            baseline_soc_stock=50.0,
            baseline_n2o_emissions=1.0,
            project_soc_stock=55.0,
            project_n2o_emissions=0.8,
        )
        self.assertEqual(data.uncertainty_deduction, 0.15)
        self.assertEqual(data.baseline_soc_stock, 50.0)

    def test_project_full(self):
        from models.project import Project, ProjectInfo, ProjectData
        from datetime import date
        info = ProjectInfo(
            project_title="P",
            proponent_name="A",
            proponent_contact="a@b.com",
            country="US",
            project_area_hectares=100.0,
            project_start_date=date(2025, 1, 1),
            crediting_period_start=date(2025, 1, 1),
            crediting_period_end=date(2032, 1, 1),
            crediting_period_years=7,
        )
        data = ProjectData(
            baseline_soc_stock=50.0,
            baseline_n2o_emissions=1.0,
            project_soc_stock=55.0,
            project_n2o_emissions=0.8,
        )
        project = Project(info=info, data=data)
        self.assertEqual(project.info.project_title, "P")
        self.assertIsNone(project.project_description)
        self.assertIsNone(project.calculations)


class TestMethodologyModels(unittest.TestCase):
    """Tests for models.methodology."""

    def test_parameter(self):
        from models.methodology import Parameter
        p = Parameter(id="SOC", name="Soil Organic Carbon", unit="tC/ha", required=True)
        self.assertEqual(p.id, "SOC")
        self.assertEqual(p.unit, "tC/ha")

    def test_equation(self):
        from models.methodology import Equation
        e = Equation(id="eq1", name="SOC", formula="A*B", inputs=["A", "B"], output="C")
        self.assertEqual(e.inputs, ["A", "B"])
        self.assertEqual(e.output, "C")

    def test_methodology(self):
        from models.methodology import Methodology, Parameter, Equation
        params = {"p1": Parameter(id="p1", name="P1", unit="t", required=True)}
        eqs = {"e1": Equation(id="e1", name="E1", formula="x", inputs=["p1"], output="out")}
        m = Methodology(id="VM0042", version="2.0", title="Agriculture", parameters=params, equations=eqs)
        self.assertEqual(m.id, "VM0042")
        order = m.get_calculation_order()
        self.assertIsInstance(order, list)
        self.assertIn("soc_sequestration", order)


class TestEvidenceModel(unittest.TestCase):
    """Tests for models.evidence."""

    def test_evidence(self):
        from models.evidence import Evidence
        e = Evidence(
            id="ev1",
            title="Report 2025",
            description="Study data",
            supports_sections=[],
        )
        self.assertEqual(e.id, "ev1")
        self.assertEqual(e.title, "Report 2025")
        self.assertEqual(e.description, "Study data")
        self.assertEqual(e.supports_sections, [])
