"""
test_ssis_parser.py — Tests for SSIS AST Parser (Trilha 3)
"""
import pytest

from src.shared.pipeline_ast.parsers.ssis_parser import SSISASTParser, SSISParseResult

# ---------------------------------------------------------------------------
# Minimal valid SSIS .dtsx XML fixture
# ---------------------------------------------------------------------------

MINIMAL_DTSX = """<?xml version="1.0"?>
<DTS:Executable
  xmlns:DTS="www.microsoft.com/SqlServer/Dts"
  DTS:ObjectName="ETL_Orders"
  DTS:CreationName="MSDTS.Package.1">

  <DTS:ConnectionManagers>
    <DTS:ConnectionManager
      DTS:ObjectName="SourceDB"
      DTS:CreationName="OLEDB">
      <DTS:ObjectData>
        <DTS:ConnectionManager
          DTS:ObjectName="SourceDB">
          <DTS:Property DTS:Name="ConnectionString">Data Source=server01;Initial Catalog=NorthWind;Provider=SQLNCLI11;</DTS:Property>
        </DTS:ConnectionManager>
      </DTS:ObjectData>
    </DTS:ConnectionManager>
  </DTS:ConnectionManagers>

  <DTS:Variables>
    <DTS:Variable DTS:ObjectName="LoadDate" DTS:Namespace="User">
      <DTS:VariableValue>2024-01-01</DTS:VariableValue>
    </DTS:Variable>
  </DTS:Variables>

  <DTS:Executables>
    <DTS:Executable
      DTS:ObjectName="Load Orders"
      DTS:CreationName="Microsoft.Pipeline">
    </DTS:Executable>
    <DTS:Executable
      DTS:ObjectName="Send Email"
      DTS:CreationName="STOCK:SendMailTask">
    </DTS:Executable>
  </DTS:Executables>

</DTS:Executable>
"""

INVALID_XML = "<not valid xml <<<<"


class TestSSISASTParser:
    def test_parse_minimal_package(self):
        parser = SSISASTParser()
        result = parser.parse_xml(MINIMAL_DTSX, package_name="ETL_Orders")
        assert isinstance(result, SSISParseResult)

    def test_package_name_preserved(self):
        parser = SSISASTParser()
        result = parser.parse_xml(MINIMAL_DTSX, package_name="ETL_Orders")
        assert result.package_name == "ETL_Orders"
        assert result.pipeline.pipeline_name == "ETL_Orders"

    def test_source_platform_is_ssis(self):
        parser = SSISASTParser()
        result = parser.parse_xml(MINIMAL_DTSX, package_name="p")
        assert result.pipeline.source_platform == "SSIS"

    def test_connection_counted(self):
        parser = SSISASTParser()
        result = parser.parse_xml(MINIMAL_DTSX, package_name="p")
        assert result.connection_count >= 1

    def test_variable_counted(self):
        parser = SSISASTParser()
        result = parser.parse_xml(MINIMAL_DTSX, package_name="p")
        assert result.variable_count >= 1

    def test_executables_counted(self):
        parser = SSISASTParser()
        result = parser.parse_xml(MINIMAL_DTSX, package_name="p")
        # One DataFlow + one ControlFlow task
        assert result.data_flow_task_count + result.control_flow_task_count >= 1

    def test_ast_coverage_between_0_and_1(self):
        parser = SSISASTParser()
        result = parser.parse_xml(MINIMAL_DTSX, package_name="p")
        assert 0.0 <= result.ast_coverage <= 1.0

    def test_invalid_xml_returns_error(self):
        parser = SSISASTParser()
        result = parser.parse_xml(INVALID_XML, package_name="broken")
        assert len(result.parse_errors) > 0

    def test_pipeline_serializable(self):
        import json
        parser = SSISASTParser()
        result = parser.parse_xml(MINIMAL_DTSX, package_name="p")
        j = result.pipeline.to_json()
        data = json.loads(j)
        assert "pipeline_id" in data

    def test_target_platform_propagated(self):
        parser = SSISASTParser()
        result = parser.parse_xml(MINIMAL_DTSX, package_name="p", target_platform="ADF")
        assert result.pipeline.target_platform == "ADF"

    def test_parse_file(self, tmp_path):
        dtsx_file = tmp_path / "ETL_Orders.dtsx"
        dtsx_file.write_text(MINIMAL_DTSX, encoding="utf-8")
        parser = SSISASTParser()
        result = parser.parse_file(dtsx_file)
        assert result.package_name == "ETL_Orders"
