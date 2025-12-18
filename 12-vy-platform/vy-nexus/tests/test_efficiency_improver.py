"""Tests for Shortcut and Efficiency Improvement System"""

import pytest
import os
import sqlite3
from datetime import datetime
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.efficiency_improver import (
    ShortcutIdentifier, EfficiencyAnalyzer, EfficiencyImprovementEngine,
    Shortcut, EfficiencyMetric, WorkflowOptimization
)


@pytest.fixture
def test_db():
    """Create a temporary test database"""
    db_path = 'data/test_efficiency.db'
    os.makedirs('data', exist_ok=True)
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    yield db_path
    
    if os.path.exists(db_path):
        os.remove(db_path)


def test_shortcut_identifier_init(test_db):
    """Test ShortcutIdentifier initialization"""
    identifier = ShortcutIdentifier(test_db)
    assert os.path.exists(test_db)
    
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shortcuts'")
    assert cursor.fetchone() is not None
    conn.close()


def test_identify_keyboard_shortcuts(test_db):
    """Test keyboard shortcut identification"""
    identifier = ShortcutIdentifier(test_db)
    
    workflow_steps = [
        "Click menu File",
        "Click Save",
        "Right click on item",
        "Copy and paste text",
        "Find text in document"
    ]
    
    shortcuts = identifier.identify_keyboard_shortcuts(workflow_steps)
    assert len(shortcuts) > 0
    assert all(s.shortcut_type == 'keyboard' for s in shortcuts)
    assert all(s.time_saved_per_use > 0 for s in shortcuts)


def test_identify_workflow_shortcuts(test_db):
    """Test workflow shortcut identification"""
    identifier = ShortcutIdentifier(test_db)
    
    # Create workflow with repeated pattern
    workflow_steps = [
        "Open file",
        "Read data",
        "Process data",
        "Open file",
        "Read data",
        "Process data",
        "Save results"
    ]
    
    shortcuts = identifier.identify_workflow_shortcuts(workflow_steps)
    assert len(shortcuts) > 0
    assert any(s.shortcut_type == 'workflow' for s in shortcuts)


def test_identify_automation_opportunities(test_db):
    """Test automation opportunity identification"""
    identifier = ShortcutIdentifier(test_db)
    
    task_history = [
        {'type': 'data_export', 'duration': 5.0},
        {'type': 'data_export', 'duration': 4.5},
        {'type': 'data_export', 'duration': 5.5},
        {'type': 'report_generation', 'duration': 10.0},
        {'type': 'report_generation', 'duration': 9.5},
        {'type': 'report_generation', 'duration': 10.5},
    ]
    
    shortcuts = identifier.identify_automation_opportunities(task_history)
    assert len(shortcuts) >= 2  # Should identify both task types
    assert all(s.shortcut_type == 'automation' for s in shortcuts)


def test_identify_caching_opportunities(test_db):
    """Test caching opportunity identification"""
    identifier = ShortcutIdentifier(test_db)
    
    data_access_patterns = [
        {'data_id': 'user_profile_123'},
        {'data_id': 'user_profile_123'},
        {'data_id': 'user_profile_123'},
        {'data_id': 'user_profile_123'},
        {'data_id': 'user_profile_123'},
        {'data_id': 'config_data'},
        {'data_id': 'config_data'},
    ]
    
    shortcuts = identifier.identify_caching_opportunities(data_access_patterns)
    assert len(shortcuts) >= 1  # Should identify user_profile_123
    assert all(s.shortcut_type == 'caching' for s in shortcuts)


def test_identify_parallelization_opportunities(test_db):
    """Test parallelization opportunity identification"""
    identifier = ShortcutIdentifier(test_db)
    
    workflow_steps = [
        {'id': 'step1', 'name': 'Fetch data A', 'duration': 2.0, 'dependencies': []},
        {'id': 'step2', 'name': 'Fetch data B', 'duration': 3.0, 'dependencies': []},
        {'id': 'step3', 'name': 'Fetch data C', 'duration': 2.5, 'dependencies': []},
        {'id': 'step4', 'name': 'Combine data', 'duration': 1.0, 'dependencies': ['step1', 'step2', 'step3']},
    ]
    
    shortcuts = identifier.identify_parallelization_opportunities(workflow_steps)
    assert len(shortcuts) > 0
    assert all(s.shortcut_type == 'parallel' for s in shortcuts)
    assert all(s.time_saved_per_use > 0 for s in shortcuts)


def test_save_and_retrieve_shortcuts(test_db):
    """Test saving and retrieving shortcuts"""
    identifier = ShortcutIdentifier(test_db)
    
    shortcut = Shortcut(
        shortcut_id='test_shortcut_1',
        shortcut_type='keyboard',
        title='Test Shortcut',
        description='A test shortcut',
        original_steps=['Step 1', 'Step 2'],
        optimized_steps=['Shortcut'],
        time_saved_per_use=2.0,
        complexity_reduction=50.0,
        implementation_code=None,
        prerequisites=[],
        created_at=datetime.now().isoformat(),
        status='identified'
    )
    
    identifier._save_shortcut(shortcut)
    
    retrieved = identifier.get_shortcuts(shortcut_type='keyboard')
    assert len(retrieved) > 0
    assert retrieved[0].shortcut_id == 'test_shortcut_1'


def test_efficiency_analyzer_init(test_db):
    """Test EfficiencyAnalyzer initialization"""
    analyzer = EfficiencyAnalyzer(test_db)
    assert os.path.exists(test_db)
    
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='efficiency_metrics'")
    assert cursor.fetchone() is not None
    conn.close()


def test_measure_improvement(test_db):
    """Test efficiency improvement measurement"""
    analyzer = EfficiencyAnalyzer(test_db)
    
    metric = analyzer.measure_improvement(
        process_id='test_process',
        metric_type='time',
        before_value=10.0,
        after_value=5.0
    )
    
    assert metric.improvement_percentage == 50.0
    assert metric.before_value == 10.0
    assert metric.after_value == 5.0


def test_get_improvement_summary(test_db):
    """Test improvement summary generation"""
    analyzer = EfficiencyAnalyzer(test_db)
    
    # Record multiple improvements
    analyzer.measure_improvement('proc1', 'time', 10.0, 5.0)
    analyzer.measure_improvement('proc1', 'time', 8.0, 4.0)
    analyzer.measure_improvement('proc1', 'steps', 20, 10)
    
    summary = analyzer.get_improvement_summary('proc1')
    
    assert 'time' in summary
    assert 'steps' in summary
    assert summary['time']['measurement_count'] == 2
    assert summary['steps']['measurement_count'] == 1


def test_efficiency_improvement_engine_init(test_db):
    """Test EfficiencyImprovementEngine initialization"""
    engine = EfficiencyImprovementEngine(test_db)
    assert os.path.exists(test_db)
    
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workflow_optimizations'")
    assert cursor.fetchone() is not None
    conn.close()


def test_analyze_workflow(test_db):
    """Test comprehensive workflow analysis"""
    engine = EfficiencyImprovementEngine(test_db)
    
    workflow_steps = [
        "Click menu File",
        "Click Save",
        "Copy and paste text",
        "Open file",
        "Read data",
        "Open file",
        "Read data"
    ]
    
    task_history = [
        {'type': 'export', 'duration': 5.0},
        {'type': 'export', 'duration': 4.5},
        {'type': 'export', 'duration': 5.5},
    ]
    
    analysis = engine.analyze_workflow('test_workflow', workflow_steps, task_history)
    
    assert analysis['workflow_id'] == 'test_workflow'
    assert 'shortcuts_identified' in analysis
    assert 'shortcuts_by_type' in analysis
    assert 'total_time_saved_per_execution' in analysis
    assert 'recommendations' in analysis


def test_generate_recommendations(test_db):
    """Test recommendation generation"""
    engine = EfficiencyImprovementEngine(test_db)
    
    shortcuts = [
        Shortcut(
            shortcut_id='s1',
            shortcut_type='keyboard',
            title='Shortcut 1',
            description='High impact',
            original_steps=['Step'],
            optimized_steps=['Shortcut'],
            time_saved_per_use=3.0,
            complexity_reduction=50.0,
            implementation_code=None,
            prerequisites=[],
            created_at=datetime.now().isoformat(),
            status='identified'
        ),
        Shortcut(
            shortcut_id='s2',
            shortcut_type='automation',
            title='Shortcut 2',
            description='Medium impact',
            original_steps=['Step'],
            optimized_steps=['Auto'],
            time_saved_per_use=1.5,
            complexity_reduction=30.0,
            implementation_code=None,
            prerequisites=[],
            created_at=datetime.now().isoformat(),
            status='identified'
        )
    ]
    
    recommendations = engine._generate_recommendations(shortcuts)
    assert len(recommendations) > 0
    assert any('high-impact' in r.lower() for r in recommendations)


def test_get_top_shortcuts(test_db):
    """Test retrieving top shortcuts"""
    engine = EfficiencyImprovementEngine(test_db)
    
    # Create some shortcuts
    workflow_steps = [
        "Click menu",
        "Save file",
        "Copy text",
        "Paste text"
    ]
    
    engine.analyze_workflow('test', workflow_steps)
    
    top_shortcuts = engine.get_top_shortcuts(limit=5)
    assert len(top_shortcuts) <= 5
    
    # Verify sorted by time savings
    if len(top_shortcuts) > 1:
        for i in range(len(top_shortcuts) - 1):
            assert top_shortcuts[i].time_saved_per_use >= top_shortcuts[i+1].time_saved_per_use


def test_shortcut_status_filtering(test_db):
    """Test filtering shortcuts by status"""
    identifier = ShortcutIdentifier(test_db)
    
    # Create shortcuts with different statuses
    for i, status in enumerate(['identified', 'implemented', 'tested']):
        shortcut = Shortcut(
            shortcut_id=f'shortcut_{i}',
            shortcut_type='keyboard',
            title=f'Shortcut {i}',
            description='Test',
            original_steps=['Step'],
            optimized_steps=['Shortcut'],
            time_saved_per_use=1.0,
            complexity_reduction=20.0,
            implementation_code=None,
            prerequisites=[],
            created_at=datetime.now().isoformat(),
            status=status
        )
        identifier._save_shortcut(shortcut)
    
    identified = identifier.get_shortcuts(status='identified')
    implemented = identifier.get_shortcuts(status='implemented')
    
    assert len(identified) >= 1
    assert len(implemented) >= 1
    assert all(s.status == 'identified' for s in identified)
    assert all(s.status == 'implemented' for s in implemented)


def test_complexity_reduction_calculation(test_db):
    """Test complexity reduction metrics"""
    identifier = ShortcutIdentifier(test_db)
    
    workflow_steps = [
        "Step 1",
        "Step 2",
        "Step 3",
        "Step 1",
        "Step 2",
        "Step 3"
    ]
    
    shortcuts = identifier.identify_workflow_shortcuts(workflow_steps)
    
    if shortcuts:
        assert all(0 <= s.complexity_reduction <= 100 for s in shortcuts)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
