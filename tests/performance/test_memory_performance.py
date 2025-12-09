"""Performance Tests for Task Memory Operations.

This module benchmarks task memory operations at scale:
- Create/read/list operations with 100, 1000, 10000 memory files
- Operation time targets: <50ms for most operations
- Search performance across large memory sets
- Memory footprint and resource usage
"""

import pytest
import time
from specify_cli.memory import TaskMemoryStore, LifecycleManager
from specify_cli.memory.injector import ContextInjector
import statistics


@pytest.fixture
def perf_project(tmp_path):
    """Create project structure for performance testing."""
    backlog_dir = tmp_path / "backlog" / "memory"
    archive_dir = backlog_dir / "archive"
    template_dir = tmp_path / "templates" / "memory"

    backlog_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)
    template_dir.mkdir(parents=True)

    # Create template
    template_content = """# Task Memory: {task_id}

**Created**: {created_date}
**Last Updated**: {updated_date}
**Task**: {task_title}

## Context
Task context for {task_id}

## Key Decisions
Decision tracking

## Approaches Tried
Approach documentation

## Open Questions
Question tracking

## Resources
Resource links

## Notes
Implementation notes
"""
    (template_dir / "default.md").write_text(template_content)

    return tmp_path


@pytest.fixture
def perf_store(perf_project):
    """Create TaskMemoryStore for performance testing."""
    return TaskMemoryStore(base_path=perf_project)


@pytest.fixture
def perf_manager(perf_store):
    """Create LifecycleManager for performance testing."""
    return LifecycleManager(store=perf_store)


def benchmark_operation(operation, iterations=100):
    """Benchmark an operation and return statistics.

    Args:
        operation: Callable to benchmark
        iterations: Number of times to run operation

    Returns:
        dict with min, max, mean, median, p95, p99 times in milliseconds
    """
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        operation()
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to milliseconds

    return {
        "min": min(times),
        "max": max(times),
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "p95": sorted(times)[int(len(times) * 0.95)],
        "p99": sorted(times)[int(len(times) * 0.99)],
        "iterations": iterations,
    }


class TestCreatePerformance:
    """Performance tests for memory creation."""

    def test_create_single_memory_performance(self, perf_store):
        """Test single memory creation performance (<50ms target)."""

        def create_memory():
            task_id = f"task-{int(time.time() * 1000000)}"
            perf_store.create(task_id, task_title="Test Task")

        stats = benchmark_operation(create_memory, iterations=100)

        # Verify performance targets
        assert stats["mean"] < 50, (
            f"Mean create time {stats['mean']:.2f}ms exceeds 50ms"
        )
        assert stats["p95"] < 100, f"P95 create time {stats['p95']:.2f}ms exceeds 100ms"

        print(
            f"\nCreate Performance: mean={stats['mean']:.2f}ms, p95={stats['p95']:.2f}ms"
        )

    def test_create_100_memories_bulk(self, perf_manager):
        """Test creating 100 memories in bulk."""
        start = time.perf_counter()

        for i in range(100):
            task_id = f"task-bulk-{i:03d}"
            perf_manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title=f"Bulk Task {i}",
            )

        duration = (time.perf_counter() - start) * 1000

        # Target: <5 seconds for 100 memories
        assert duration < 5000, (
            f"Creating 100 memories took {duration:.2f}ms, target <5000ms"
        )

        # Average per-memory time
        avg_time = duration / 100
        assert avg_time < 50, f"Average create time {avg_time:.2f}ms exceeds 50ms"

        print(f"\nBulk Create 100: total={duration:.2f}ms, avg={avg_time:.2f}ms")

    @pytest.mark.slow
    def test_create_1000_memories_bulk(self, perf_manager):
        """Test creating 1000 memories in bulk."""
        start = time.perf_counter()

        for i in range(1000):
            task_id = f"task-bulk1k-{i:04d}"
            perf_manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title=f"Bulk Task {i}",
            )

        duration = (time.perf_counter() - start) * 1000

        # Target: <50 seconds for 1000 memories
        assert duration < 50000, f"Creating 1000 memories took {duration:.2f}ms"

        avg_time = duration / 1000
        assert avg_time < 50, f"Average create time {avg_time:.2f}ms exceeds 50ms"

        print(f"\nBulk Create 1000: total={duration:.2f}ms, avg={avg_time:.2f}ms")


class TestReadPerformance:
    """Performance tests for memory reading."""

    @pytest.fixture
    def populated_store(self, perf_manager, perf_store):
        """Create store with 100 pre-populated memories."""
        for i in range(100):
            task_id = f"task-read-{i:03d}"
            perf_manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title=f"Read Test {i}",
            )
            perf_store.append(task_id, f"Content for task {i}")

        return perf_store

    def test_read_single_memory_performance(self, populated_store):
        """Test single memory read performance (<50ms target)."""
        task_id = "task-read-050"

        def read_memory():
            content = populated_store.read(task_id)
            assert len(content) > 0

        stats = benchmark_operation(read_memory, iterations=100)

        assert stats["mean"] < 50, f"Mean read time {stats['mean']:.2f}ms exceeds 50ms"
        assert stats["p95"] < 100, f"P95 read time {stats['p95']:.2f}ms exceeds 100ms"

        print(
            f"\nRead Performance: mean={stats['mean']:.2f}ms, p95={stats['p95']:.2f}ms"
        )

    def test_read_100_memories_sequential(self, populated_store):
        """Test reading 100 memories sequentially."""
        start = time.perf_counter()

        for i in range(100):
            task_id = f"task-read-{i:03d}"
            content = populated_store.read(task_id)
            assert len(content) > 0

        duration = (time.perf_counter() - start) * 1000

        # Target: <5 seconds for 100 reads
        assert duration < 5000, f"Reading 100 memories took {duration:.2f}ms"

        avg_time = duration / 100
        assert avg_time < 50, f"Average read time {avg_time:.2f}ms exceeds 50ms"

        print(f"\nBulk Read 100: total={duration:.2f}ms, avg={avg_time:.2f}ms")


class TestListPerformance:
    """Performance tests for listing memories."""

    @pytest.fixture
    def large_store_100(self, perf_manager, perf_store):
        """Store with 100 memories."""
        for i in range(100):
            task_id = f"task-list100-{i:03d}"
            perf_manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title=f"List Test {i}",
            )
        return perf_store

    @pytest.fixture
    def large_store_1000(self, perf_manager, perf_store):
        """Store with 1000 memories."""
        for i in range(1000):
            task_id = f"task-list1k-{i:04d}"
            perf_manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title=f"List Test {i}",
            )
        return perf_store

    def test_list_100_memories_performance(self, large_store_100):
        """Test listing 100 memories (<50ms target)."""

        def list_memories():
            memories = large_store_100.list_active()
            assert len(memories) == 100

        stats = benchmark_operation(list_memories, iterations=50)

        assert stats["mean"] < 50, f"Mean list time {stats['mean']:.2f}ms exceeds 50ms"
        assert stats["p95"] < 100, f"P95 list time {stats['p95']:.2f}ms exceeds 100ms"

        print(
            f"\nList 100 Performance: mean={stats['mean']:.2f}ms, p95={stats['p95']:.2f}ms"
        )

    @pytest.mark.slow
    def test_list_1000_memories_performance(self, large_store_1000):
        """Test listing 1000 memories (<200ms target)."""

        def list_memories():
            memories = large_store_1000.list_active()
            assert len(memories) == 1000

        stats = benchmark_operation(list_memories, iterations=20)

        assert stats["mean"] < 200, (
            f"Mean list time {stats['mean']:.2f}ms exceeds 200ms"
        )
        assert stats["p95"] < 500, f"P95 list time {stats['p95']:.2f}ms exceeds 500ms"

        print(
            f"\nList 1000 Performance: mean={stats['mean']:.2f}ms, p95={stats['p95']:.2f}ms"
        )


@pytest.mark.skip(reason="TaskMemoryStore has no search method - search is CLI-only")
class TestSearchPerformance:
    """Performance tests for searching memory content."""

    @pytest.fixture
    def searchable_store(self, perf_manager, perf_store):
        """Store with searchable content."""
        keywords = ["backend", "frontend", "database", "api", "security"]

        for i in range(100):
            task_id = f"task-search-{i:03d}"
            perf_manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title=f"Search Test {i}",
            )

            # Add searchable content
            keyword = keywords[i % len(keywords)]
            perf_store.append(task_id, f"Implementation uses {keyword} technology")
            perf_store.append(task_id, f"Key decision: {keyword} approach selected")

        return perf_store

    def test_search_100_memories_performance(self, searchable_store):
        """Test searching across 100 memories (<100ms target)."""

        def search_memories():
            results = searchable_store.search("backend")
            assert len(results) >= 0  # May or may not find matches

        stats = benchmark_operation(search_memories, iterations=20)

        assert stats["mean"] < 100, (
            f"Mean search time {stats['mean']:.2f}ms exceeds 100ms"
        )
        assert stats["p95"] < 200, f"P95 search time {stats['p95']:.2f}ms exceeds 200ms"

        print(
            f"\nSearch 100 Performance: mean={stats['mean']:.2f}ms, p95={stats['p95']:.2f}ms"
        )

    def test_search_multiple_keywords(self, searchable_store):
        """Test searching with multiple keywords."""
        keywords = ["backend", "frontend", "database"]

        start = time.perf_counter()

        for keyword in keywords:
            results = searchable_store.search(keyword)
            assert isinstance(results, list)

        duration = (time.perf_counter() - start) * 1000

        # Target: <300ms for 3 searches
        assert duration < 300, f"Multi-keyword search took {duration:.2f}ms"

        print(f"\nMulti-Keyword Search: {duration:.2f}ms for {len(keywords)} keywords")


class TestAppendPerformance:
    """Performance tests for appending content to memories."""

    @pytest.fixture
    def append_store(self, perf_manager, perf_store):
        """Store with memories ready for appending."""
        for i in range(10):
            task_id = f"task-append-{i:02d}"
            perf_manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title=f"Append Test {i}",
            )
        return perf_store

    def test_append_single_performance(self, append_store):
        """Test single append operation (<50ms target)."""
        task_id = "task-append-05"

        def append_content():
            append_store.append(task_id, f"Entry at {time.time()}")

        stats = benchmark_operation(append_content, iterations=100)

        assert stats["mean"] < 50, (
            f"Mean append time {stats['mean']:.2f}ms exceeds 50ms"
        )
        assert stats["p95"] < 100, f"P95 append time {stats['p95']:.2f}ms exceeds 100ms"

        print(
            f"\nAppend Performance: mean={stats['mean']:.2f}ms, p95={stats['p95']:.2f}ms"
        )

    def test_append_bulk_100_entries(self, append_store):
        """Test appending 100 entries to same memory."""
        task_id = "task-append-00"

        start = time.perf_counter()

        for i in range(100):
            append_store.append(task_id, f"Entry {i}: Additional content")

        duration = (time.perf_counter() - start) * 1000

        # Target: <5 seconds for 100 appends
        assert duration < 5000, f"100 appends took {duration:.2f}ms"

        avg_time = duration / 100
        assert avg_time < 50, f"Average append time {avg_time:.2f}ms exceeds 50ms"

        print(f"\nBulk Append 100: total={duration:.2f}ms, avg={avg_time:.2f}ms")


class TestArchivePerformance:
    """Performance tests for archiving operations."""

    @pytest.fixture
    def archive_store(self, perf_manager, perf_store):
        """Store with memories ready for archiving."""
        for i in range(100):
            task_id = f"task-archive-{i:03d}"
            perf_manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title=f"Archive Test {i}",
            )
        return perf_store, perf_manager

    def test_archive_single_performance(self, archive_store):
        """Test single archive operation (<50ms target)."""
        store, manager = archive_store

        task_ids = [f"task-archive-{i:03d}" for i in range(10)]
        idx = 0

        def archive_memory():
            nonlocal idx
            if idx >= len(task_ids):
                idx = 0
            task_id = task_ids[idx]
            idx += 1

            # Archive by state change
            manager.on_state_change(
                task_id=task_id,
                old_state="In Progress",
                new_state="Done",
                task_title="Archive Test",
            )

        stats = benchmark_operation(archive_memory, iterations=10)

        assert stats["mean"] < 50, (
            f"Mean archive time {stats['mean']:.2f}ms exceeds 50ms"
        )
        assert stats["p95"] < 100, (
            f"P95 archive time {stats['p95']:.2f}ms exceeds 100ms"
        )

        print(
            f"\nArchive Performance: mean={stats['mean']:.2f}ms, p95={stats['p95']:.2f}ms"
        )

    def test_archive_bulk_100_memories(self, archive_store):
        """Test archiving 100 memories in bulk."""
        store, manager = archive_store

        start = time.perf_counter()

        for i in range(100):
            task_id = f"task-archive-{i:03d}"
            manager.on_state_change(
                task_id=task_id,
                old_state="In Progress",
                new_state="Done",
                task_title=f"Archive Test {i}",
            )

        duration = (time.perf_counter() - start) * 1000

        # Target: <5 seconds for 100 archives
        assert duration < 5000, f"Archiving 100 memories took {duration:.2f}ms"

        avg_time = duration / 100
        assert avg_time < 50, f"Average archive time {avg_time:.2f}ms exceeds 50ms"

        print(f"\nBulk Archive 100: total={duration:.2f}ms, avg={avg_time:.2f}ms")


@pytest.mark.skip(
    reason="Uses wrong API (project_root vs base_path) and non-existent inject_active_tasks method"
)
class TestInjectionPerformance:
    """Performance tests for context injection."""

    @pytest.fixture
    def injection_store(self, perf_project, perf_manager):
        """Store with many active tasks for injection testing."""
        # Create CLAUDE.md
        claude_dir = perf_project / ".claude"
        claude_dir.mkdir(exist_ok=True)
        (claude_dir / "CLAUDE.md").write_text("""# Project

@import backlog/memory/active-tasks.md
""")

        # Create many tasks
        for i in range(100):
            task_id = f"task-inject-{i:03d}"
            perf_manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title=f"Inject Test {i}",
            )

        return ContextInjector(project_root=perf_project)

    def test_inject_100_tasks_performance(self, injection_store):
        """Test injecting 100 active tasks (<100ms target)."""

        def inject_context():
            injection_store.inject_active_tasks()

        stats = benchmark_operation(inject_context, iterations=10)

        assert stats["mean"] < 100, (
            f"Mean injection time {stats['mean']:.2f}ms exceeds 100ms"
        )
        assert stats["p95"] < 200, (
            f"P95 injection time {stats['p95']:.2f}ms exceeds 200ms"
        )

        print(
            f"\nInjection 100 Tasks: mean={stats['mean']:.2f}ms, p95={stats['p95']:.2f}ms"
        )


class TestScalabilityEdgeCases:
    """Tests for scalability edge cases and limits."""

    @pytest.mark.slow
    @pytest.mark.skipif(True, reason="Very slow test, run manually for stress testing")
    def test_create_10000_memories(self, perf_manager):
        """Stress test: Create 10,000 memories."""
        start = time.perf_counter()

        for i in range(10000):
            task_id = f"task-stress-{i:05d}"
            perf_manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title=f"Stress Test {i}",
            )

        duration = (time.perf_counter() - start) * 1000

        avg_time = duration / 10000

        print(f"\nStress Test 10,000: total={duration:.2f}ms, avg={avg_time:.2f}ms")

        # Should still maintain reasonable performance
        assert avg_time < 100, f"Average time {avg_time:.2f}ms degraded significantly"

    def test_large_memory_content(self, perf_store, perf_manager):
        """Test performance with large memory content (10KB)."""
        task_id = "task-large-content"

        perf_manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Large Content Test",
        )

        # Append 10KB of content
        large_content = "x" * 10240  # 10KB

        start = time.perf_counter()
        perf_store.append(task_id, large_content)
        append_duration = (time.perf_counter() - start) * 1000

        # Read large content
        start = time.perf_counter()
        content = perf_store.read(task_id)
        read_duration = (time.perf_counter() - start) * 1000

        assert large_content in content

        # Should handle large content reasonably
        assert append_duration < 100, f"Large append took {append_duration:.2f}ms"
        assert read_duration < 100, f"Large read took {read_duration:.2f}ms"

        print(
            f"\nLarge Content (10KB): append={append_duration:.2f}ms, read={read_duration:.2f}ms"
        )

    def test_many_small_appends(self, perf_store, perf_manager):
        """Test performance with many small appends."""
        task_id = "task-many-appends"

        perf_manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Many Appends Test",
        )

        # 1000 small appends
        start = time.perf_counter()

        for i in range(1000):
            perf_store.append(task_id, f"Entry {i}")

        duration = (time.perf_counter() - start) * 1000

        # Should complete in reasonable time
        assert duration < 50000, f"1000 appends took {duration:.2f}ms, target <50s"

        avg_time = duration / 1000
        print(f"\n1000 Small Appends: total={duration:.2f}ms, avg={avg_time:.2f}ms")


class TestMemoryFootprint:
    """Tests for memory footprint and resource usage."""

    def test_memory_file_size_reasonable(self, perf_store, perf_manager):
        """Test that memory files don't grow unreasonably large."""
        task_id = "task-filesize"

        perf_manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="File Size Test",
        )

        # Add typical amount of content
        for i in range(50):
            perf_store.append(
                task_id, f"Entry {i}: Some implementation notes about feature X"
            )

        memory_path = perf_store.get_path(task_id)
        file_size = memory_path.stat().st_size

        # Should be under 50KB for typical usage
        assert file_size < 50 * 1024, f"Memory file is {file_size} bytes, target <50KB"

        print(f"\nMemory File Size: {file_size} bytes ({file_size / 1024:.2f} KB)")

    def test_archive_directory_growth(self, perf_manager, perf_store):
        """Test archive directory doesn't grow unbounded."""
        # Create and archive 100 tasks
        for i in range(100):
            task_id = f"task-growth-{i:03d}"
            perf_manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title=f"Growth Test {i}",
            )
            perf_manager.on_state_change(
                task_id=task_id,
                old_state="In Progress",
                new_state="Done",
                task_title=f"Growth Test {i}",
            )

        # Check archive size

        total_size = sum(f.stat().st_size for f in perf_store.archive_dir.glob("*.md"))

        # Should be reasonable (under 5MB for 100 files)
        assert total_size < 5 * 1024 * 1024, (
            f"Archive is {total_size} bytes, target <5MB"
        )

        print(
            f"\nArchive Size (100 files): {total_size} bytes ({total_size / 1024 / 1024:.2f} MB)"
        )
