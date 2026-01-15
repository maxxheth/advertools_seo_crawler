"""
Report Cleanup - Manages report retention and cleanup
"""
import os
import gzip
import bz2
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List


class ReportCleanup:
    """Manages report retention and cleanup policies."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize report cleanup manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.retention_days = config.get('report_retention', {}).get('days', 30)
        self.compression = config.get('report_retention', {}).get('compression', 'gzip')
        self.auto_cleanup = config.get('report_retention', {}).get('auto_cleanup', True)
        self.reports_dir = Path(config.get('analysis_settings', {}).get('report_storage', '/app/reports'))

    def cleanup_old_reports(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Clean up reports older than retention period.

        Args:
            dry_run: If True, only report what would be deleted without deleting

        Returns:
            Cleanup results
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_files = []
        deleted_size = 0

        for report_file in self.reports_dir.rglob("report_*.json*"):
            file_stat = report_file.stat()
            file_mtime = datetime.fromtimestamp(file_stat.st_mtime)

            if file_mtime < cutoff_date:
                deleted_size += file_stat.st_size

                if not dry_run:
                    try:
                        report_file.unlink()
                        deleted_files.append(str(report_file))
                    except Exception as e:
                        print(f"Error deleting {report_file}: {e}")
                else:
                    deleted_files.append(str(report_file))

        return {
            "retention_days": self.retention_days,
            "cutoff_date": cutoff_date.isoformat(),
            "files_deleted": len(deleted_files),
            "space_freed_mb": round(deleted_size / (1024 * 1024), 2),
            "deleted_files": deleted_files,
            "dry_run": dry_run,
        }

    def compress_old_reports(self, days_old: int = 7, dry_run: bool = False) -> Dict[str, Any]:
        """
        Compress reports older than specified days.

        Args:
            days_old: Number of days before compression
            dry_run: If True, only report what would be compressed

        Returns:
            Compression results
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        compressed_files = []
        space_freed = 0

        for report_file in self.reports_dir.rglob("report_*.json"):
            if report_file.suffix == '.json':  # Only compress uncompressed files
                file_mtime = datetime.fromtimestamp(report_file.stat().st_mtime)

                if file_mtime < cutoff_date:
                    original_size = report_file.stat().st_size

                    if not dry_run:
                        try:
                            self._compress_file(report_file)
                            space_freed += original_size - Path(str(report_file) + '.gz').stat().st_size
                            compressed_files.append(str(report_file))
                        except Exception as e:
                            print(f"Error compressing {report_file}: {e}")
                    else:
                        compressed_files.append(str(report_file))

        return {
            "compression_method": self.compression,
            "days_old": days_old,
            "files_compressed": len(compressed_files),
            "space_freed_mb": round(space_freed / (1024 * 1024), 2),
            "compressed_files": compressed_files,
            "dry_run": dry_run,
        }

    def archive_crawler_reports(self, crawler_type: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Archive all reports for a specific crawler type.

        Args:
            crawler_type: Type of crawler to archive
            dry_run: If True, only report what would be archived

        Returns:
            Archive results
        """
        crawler_dir = self.reports_dir / crawler_type
        archived_files = []

        if crawler_dir.exists():
            for report_file in crawler_dir.glob("report_*.json"):
                if not dry_run:
                    try:
                        self._compress_file(report_file)
                        archived_files.append(str(report_file))
                    except Exception as e:
                        print(f"Error archiving {report_file}: {e}")
                else:
                    archived_files.append(str(report_file))

        return {
            "crawler_type": crawler_type,
            "files_archived": len(archived_files),
            "archived_files": archived_files,
            "dry_run": dry_run,
        }

    def get_report_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored reports.

        Returns:
            Report statistics
        """
        stats = {
            "total_reports": 0,
            "total_size_mb": 0,
            "by_crawler_type": {},
            "by_age": {
                "less_than_7_days": 0,
                "7_to_30_days": 0,
                "older_than_30_days": 0,
            }
        }

        now = datetime.now()

        for report_file in self.reports_dir.rglob("report_*"):
            file_size = report_file.stat().st_size
            file_mtime = datetime.fromtimestamp(report_file.stat().st_mtime)
            days_old = (now - file_mtime).days

            # Count by crawler type
            crawler_type = report_file.parent.name
            if crawler_type not in stats["by_crawler_type"]:
                stats["by_crawler_type"][crawler_type] = {"count": 0, "size_mb": 0}

            stats["by_crawler_type"][crawler_type]["count"] += 1
            stats["by_crawler_type"][crawler_type]["size_mb"] += file_size / (1024 * 1024)

            # Count by age
            if days_old < 7:
                stats["by_age"]["less_than_7_days"] += 1
            elif days_old < 30:
                stats["by_age"]["7_to_30_days"] += 1
            else:
                stats["by_age"]["older_than_30_days"] += 1

            stats["total_reports"] += 1
            stats["total_size_mb"] += file_size / (1024 * 1024)

        stats["total_size_mb"] = round(stats["total_size_mb"], 2)

        return stats

    @staticmethod
    def _compress_file(file_path: Path) -> str:
        """
        Compress a file using gzip.

        Args:
            file_path: Path to file to compress

        Returns:
            Path to compressed file
        """
        compressed_path = Path(str(file_path) + '.gz')

        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                f_out.write(f_in.read())

        file_path.unlink()
        return str(compressed_path)
