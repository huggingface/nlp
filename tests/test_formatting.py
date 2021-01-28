from unittest import TestCase

import numpy as np
import pandas as pd
import pyarrow as pa

from datasets.formatting import NumpyFormatter, PandasFormatter, PythonFormatter, query_table
from datasets.formatting.formatting import NumpyArrowExtractor, PandasArrowExtractor, PythonArrowExtractor

from .utils import require_tf, require_torch


_COL_A = [0, 1, 2]
_COL_B = ["foo", "bar", "foobar"]
_COL_C = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


class ArrowExtractorTest(TestCase):
    def _create_dummy_table(self):
        return pa.Table.from_pydict({"a": _COL_A, "b": _COL_B, "c": _COL_C})

    def test_python_extractor(self):
        pa_table = self._create_dummy_table()
        extractor = PythonArrowExtractor()
        row = extractor.extract_row(pa_table)
        self.assertEqual(row, {"a": _COL_A[0], "b": _COL_B[0], "c": _COL_C[0]})
        col = extractor.extract_column(pa_table)
        self.assertEqual(col, _COL_A)
        batch = extractor.extract_batch(pa_table)
        self.assertEqual(batch, {"a": _COL_A, "b": _COL_B, "c": _COL_C})

    def test_numpy_extractor(self):
        pa_table = self._create_dummy_table()
        extractor = NumpyArrowExtractor()
        row = extractor.extract_row(pa_table)
        np.testing.assert_equal(row, {"a": _COL_A[0], "b": _COL_B[0], "c": np.array(_COL_C[0])})
        col = extractor.extract_column(pa_table)
        np.testing.assert_equal(col, np.array(_COL_A))
        batch = extractor.extract_batch(pa_table)
        np.testing.assert_equal(batch, {"a": np.array(_COL_A), "b": np.array(_COL_B), "c": np.array(_COL_C)})

    def test_numpy_extractor_np_array_kwargs(self):
        pa_table = self._create_dummy_table().drop(["b"])
        extractor = NumpyArrowExtractor(dtype=np.float16)
        row = extractor.extract_row(pa_table)
        self.assertEqual(row["c"].dtype, np.dtype(np.float16))
        col = extractor.extract_column(pa_table)
        self.assertEqual(col.dtype, np.float16)
        batch = extractor.extract_batch(pa_table)
        self.assertEqual(batch["a"].dtype, np.dtype(np.float16))
        self.assertEqual(batch["c"].dtype, np.dtype(np.float16))

    def test_pandas_extractor(self):
        pa_table = self._create_dummy_table()
        extractor = PandasArrowExtractor()
        row = extractor.extract_row(pa_table)
        pd.testing.assert_series_equal(row["a"], pd.Series(_COL_A, name="a")[:1])
        pd.testing.assert_series_equal(row["b"], pd.Series(_COL_B, name="b")[:1])
        pd.testing.assert_series_equal(row["c"], pd.Series(_COL_C, name="c")[:1])
        col = extractor.extract_column(pa_table)
        pd.testing.assert_series_equal(col, pd.Series(_COL_A, name="a"))
        batch = extractor.extract_batch(pa_table)
        pd.testing.assert_series_equal(batch["a"], pd.Series(_COL_A, name="a"))
        pd.testing.assert_series_equal(batch["b"], pd.Series(_COL_B, name="b"))
        pd.testing.assert_series_equal(batch["c"], pd.Series(_COL_C, name="c"))


class FormatterTest(TestCase):
    def _create_dummy_table(self):
        return pa.Table.from_pydict({"a": _COL_A, "b": _COL_B, "c": _COL_C})

    def test_python_formatter(self):
        pa_table = self._create_dummy_table()
        formatter = PythonFormatter()
        row = formatter.format_row(pa_table)
        self.assertEqual(row, {"a": _COL_A[0], "b": _COL_B[0], "c": _COL_C[0]})
        col = formatter.format_column(pa_table)
        self.assertEqual(col, _COL_A)
        batch = formatter.format_batch(pa_table)
        self.assertEqual(batch, {"a": _COL_A, "b": _COL_B, "c": _COL_C})

    def test_numpy_formatter(self):
        pa_table = self._create_dummy_table()
        formatter = NumpyFormatter()
        row = formatter.format_row(pa_table)
        np.testing.assert_equal(row, {"a": _COL_A[0], "b": _COL_B[0], "c": np.array(_COL_C[0])})
        col = formatter.format_column(pa_table)
        np.testing.assert_equal(col, np.array(_COL_A))
        batch = formatter.format_batch(pa_table)
        np.testing.assert_equal(batch, {"a": np.array(_COL_A), "b": np.array(_COL_B), "c": np.array(_COL_C)})

    def test_numpy_formatter_np_array_kwargs(self):
        pa_table = self._create_dummy_table().drop(["b"])
        formatter = NumpyFormatter(dtype=np.float16)
        row = formatter.format_row(pa_table)
        self.assertEqual(row["c"].dtype, np.dtype(np.float16))
        col = formatter.format_column(pa_table)
        self.assertEqual(col.dtype, np.float16)
        batch = formatter.format_batch(pa_table)
        self.assertEqual(batch["a"].dtype, np.dtype(np.float16))
        self.assertEqual(batch["c"].dtype, np.dtype(np.float16))

    def test_pandas_formatter(self):
        pa_table = self._create_dummy_table()
        formatter = PandasFormatter()
        row = formatter.format_row(pa_table)
        pd.testing.assert_series_equal(row["a"], pd.Series(_COL_A, name="a")[:1])
        pd.testing.assert_series_equal(row["b"], pd.Series(_COL_B, name="b")[:1])
        pd.testing.assert_series_equal(row["c"], pd.Series(_COL_C, name="c")[:1])
        col = formatter.format_column(pa_table)
        pd.testing.assert_series_equal(col, pd.Series(_COL_A, name="a"))
        batch = formatter.format_batch(pa_table)
        pd.testing.assert_series_equal(batch["a"], pd.Series(_COL_A, name="a"))
        pd.testing.assert_series_equal(batch["b"], pd.Series(_COL_B, name="b"))
        pd.testing.assert_series_equal(batch["c"], pd.Series(_COL_C, name="c"))

    @require_torch
    def test_torch_formatter(self):
        import torch

        from datasets.formatting import TorchFormatter

        pa_table = self._create_dummy_table().drop(["b"])
        formatter = TorchFormatter()
        row = formatter.format_row(pa_table)
        torch.testing.assert_allclose(row["a"], torch.tensor(_COL_A, dtype=torch.int64)[0])
        torch.testing.assert_allclose(row["c"], torch.tensor(_COL_C, dtype=torch.float64)[0])
        col = formatter.format_column(pa_table)
        torch.testing.assert_allclose(col, torch.tensor(_COL_A, dtype=torch.int64))
        batch = formatter.format_batch(pa_table)
        torch.testing.assert_allclose(batch["a"], torch.tensor(_COL_A, dtype=torch.int64))
        torch.testing.assert_allclose(batch["c"], torch.tensor(_COL_C, dtype=torch.float64))

    @require_torch
    def test_torch_formatter_np_array_kwargs(self):
        import torch

        from datasets.formatting import TorchFormatter

        pa_table = self._create_dummy_table().drop(["b"])
        formatter = TorchFormatter(dtype=torch.float16)
        row = formatter.format_row(pa_table)
        self.assertEqual(row["c"].dtype, torch.float16)
        col = formatter.format_column(pa_table)
        self.assertEqual(col.dtype, torch.float16)
        batch = formatter.format_batch(pa_table)
        self.assertEqual(batch["a"].dtype, torch.float16)
        self.assertEqual(batch["c"].dtype, torch.float16)

    @require_tf
    def test_tf_formatter(self):
        import tensorflow as tf

        from datasets.formatting import TFFormatter

        pa_table = self._create_dummy_table()
        formatter = TFFormatter()
        row = formatter.format_row(pa_table)
        tf.debugging.assert_equal(row["a"], tf.ragged.constant(_COL_A, dtype=tf.int64)[0])
        tf.debugging.assert_equal(row["b"], tf.ragged.constant(_COL_B, dtype=tf.string)[0])
        tf.debugging.assert_equal(row["c"], tf.ragged.constant(_COL_C, dtype=tf.float64)[0])
        col = formatter.format_column(pa_table)
        tf.debugging.assert_equal(col, tf.ragged.constant(_COL_A, dtype=tf.int64))
        batch = formatter.format_batch(pa_table)
        tf.debugging.assert_equal(batch["a"], tf.ragged.constant(_COL_A, dtype=tf.int64))
        tf.debugging.assert_equal(batch["b"], tf.ragged.constant(_COL_B, dtype=tf.string))
        self.assertIsInstance(batch["c"], tf.RaggedTensor)
        self.assertEqual(batch["c"].dtype, tf.float64)
        tf.debugging.assert_equal(
            batch["c"].bounding_shape(), tf.ragged.constant(_COL_C, dtype=tf.float64).bounding_shape()
        )
        tf.debugging.assert_equal(batch["c"].flat_values, tf.ragged.constant(_COL_C, dtype=tf.float64).flat_values)

    @require_tf
    def test_tf_formatter_np_array_kwargs(self):
        import tensorflow as tf

        from datasets.formatting import TFFormatter

        pa_table = self._create_dummy_table().drop(["b"])
        formatter = TFFormatter(dtype=tf.float16)
        row = formatter.format_row(pa_table)
        self.assertEqual(row["c"].dtype, tf.float16)
        col = formatter.format_column(pa_table)
        self.assertEqual(col.dtype, tf.float16)
        batch = formatter.format_batch(pa_table)
        self.assertEqual(batch["a"].dtype, tf.float16)
        self.assertEqual(batch["c"].dtype, tf.float16)


class QueryTest(TestCase):
    def _create_dummy_table(self):
        return pa.Table.from_pydict({"a": _COL_A, "b": _COL_B, "c": _COL_C})

    def assertTableEqual(self, first: pa.Table, second: pa.Table):
        self.assertEqual(first.schema, second.schema)
        for first_array, second_array in zip(first, second):
            self.assertEqual(first_array, second_array)
        self.assertEqual(first, second)

    def test_query_table_int(self):
        pa_table = self._create_dummy_table()
        n = pa_table.num_rows
        subtable = query_table(pa_table, 0)
        self.assertTableEqual(subtable, pa.Table.from_pydict({"a": _COL_A[:1], "b": _COL_B[:1], "c": _COL_C[:1]}))
        subtable = query_table(pa_table, 1)
        self.assertTableEqual(subtable, pa.Table.from_pydict({"a": _COL_A[1:2], "b": _COL_B[1:2], "c": _COL_C[1:2]}))
        subtable = query_table(pa_table, -1)
        self.assertTableEqual(subtable, pa.Table.from_pydict({"a": _COL_A[-1:], "b": _COL_B[-1:], "c": _COL_C[-1:]}))
        with self.assertRaises(IndexError):
            query_table(pa_table, n)
        with self.assertRaises(IndexError):
            query_table(pa_table, -(n + 1))

    def test_query_table_slice(self):
        pa_table = self._create_dummy_table()
        n = pa_table.num_rows
        # classical usage
        subtable = query_table(pa_table, slice(0, 1))
        self.assertTableEqual(subtable, pa.Table.from_pydict({"a": _COL_A[:1], "b": _COL_B[:1], "c": _COL_C[:1]}))
        subtable = query_table(pa_table, slice(1, 2))
        self.assertTableEqual(subtable, pa.Table.from_pydict({"a": _COL_A[1:2], "b": _COL_B[1:2], "c": _COL_C[1:2]}))
        subtable = query_table(pa_table, slice(-2, -1))
        self.assertTableEqual(
            subtable, pa.Table.from_pydict({"a": _COL_A[-2:-1], "b": _COL_B[-2:-1], "c": _COL_C[-2:-1]})
        )
        # usage with None
        subtable = query_table(pa_table, slice(-1, None))
        self.assertTableEqual(subtable, pa.Table.from_pydict({"a": _COL_A[-1:], "b": _COL_B[-1:], "c": _COL_C[-1:]}))
        subtable = query_table(pa_table, slice(None, n + 1))
        self.assertTableEqual(
            subtable, pa.Table.from_pydict({"a": _COL_A[: n + 1], "b": _COL_B[: n + 1], "c": _COL_C[: n + 1]})
        )
        self.assertTableEqual(subtable, pa.Table.from_pydict({"a": _COL_A, "b": _COL_B, "c": _COL_C}))
        subtable = query_table(pa_table, slice(-(n + 1), None))
        self.assertTableEqual(
            subtable, pa.Table.from_pydict({"a": _COL_A[-(n + 1) :], "b": _COL_B[-(n + 1) :], "c": _COL_C[-(n + 1) :]})
        )
        self.assertTableEqual(subtable, pa.Table.from_pydict({"a": _COL_A, "b": _COL_B, "c": _COL_C}))
        # usage with step
        subtable = query_table(pa_table, slice(None, None, 2))
        self.assertTableEqual(subtable, pa.Table.from_pydict({"a": _COL_A[::2], "b": _COL_B[::2], "c": _COL_C[::2]}))
        # empty ouput but no errors
        subtable = query_table(pa_table, slice(-1, 0))  # usage with both negative and positive idx
        assert len(_COL_A[-1:0]) == 0
        self.assertTableEqual(subtable, pa_table.slice(0, 0))
        subtable = query_table(pa_table, slice(2, 1))
        assert len(_COL_A[2:1]) == 0
        self.assertTableEqual(subtable, pa_table.slice(0, 0))
        subtable = query_table(pa_table, slice(n, n))
        assert len(_COL_A[n:n]) == 0
        self.assertTableEqual(subtable, pa_table.slice(0, 0))
        subtable = query_table(pa_table, slice(n, n + 1))
        assert len(_COL_A[n : n + 1]) == 0
        self.assertTableEqual(subtable, pa_table.slice(0, 0))
        # it's not possible to get an error with a slice

    def test_query_table_range(self):
        pa_table = self._create_dummy_table()
        n = pa_table.num_rows
        np_A, np_B, np_C = np.array(_COL_A, dtype=np.int64), np.array(_COL_B), np.array(_COL_C)
        # classical usage
        subtable = query_table(pa_table, range(0, 1))
        self.assertTableEqual(
            subtable,
            pa.Table.from_pydict({"a": np_A[range(0, 1)], "b": np_B[range(0, 1)], "c": np_C[range(0, 1)].tolist()}),
        )
        subtable = query_table(pa_table, range(1, 2))
        self.assertTableEqual(
            subtable,
            pa.Table.from_pydict({"a": np_A[range(1, 2)], "b": np_B[range(1, 2)], "c": np_C[range(1, 2)].tolist()}),
        )
        subtable = query_table(pa_table, range(-2, -1))
        self.assertTableEqual(
            subtable,
            pa.Table.from_pydict(
                {"a": np_A[range(-2, -1)], "b": np_B[range(-2, -1)], "c": np_C[range(-2, -1)].tolist()}
            ),
        )
        # usage with both negative and positive idx
        subtable = query_table(pa_table, range(-1, 0))
        self.assertTableEqual(
            subtable,
            pa.Table.from_pydict({"a": np_A[range(-1, 0)], "b": np_B[range(-1, 0)], "c": np_C[range(-1, 0)].tolist()}),
        )
        subtable = query_table(pa_table, range(-1, n))
        self.assertTableEqual(
            subtable,
            pa.Table.from_pydict({"a": np_A[range(-1, n)], "b": np_B[range(-1, n)], "c": np_C[range(-1, n)].tolist()}),
        )
        # usage with step
        subtable = query_table(pa_table, range(0, n, 2))
        self.assertTableEqual(
            subtable,
            pa.Table.from_pydict(
                {"a": np_A[range(0, n, 2)], "b": np_B[range(0, n, 2)], "c": np_C[range(0, n, 2)].tolist()}
            ),
        )
        subtable = query_table(pa_table, range(0, n + 1, 2 * n))
        self.assertTableEqual(
            subtable,
            pa.Table.from_pydict(
                {
                    "a": np_A[range(0, n + 1, 2 * n)],
                    "b": np_B[range(0, n + 1, 2 * n)],
                    "c": np_C[range(0, n + 1, 2 * n)].tolist(),
                }
            ),
        )
        # empty ouput but no errors
        subtable = query_table(pa_table, range(2, 1))
        assert len(np_A[range(2, 1)]) == 0
        self.assertTableEqual(subtable, pa.Table.from_batches([], schema=pa_table.schema))
        subtable = query_table(pa_table, range(n, n))
        assert len(np_A[range(n, n)]) == 0
        self.assertTableEqual(subtable, pa.Table.from_batches([], schema=pa_table.schema))
        # raise an IndexError
        with self.assertRaises(IndexError):
            with self.assertRaises(IndexError):
                np_A[range(0, n + 1)]
            query_table(pa_table, range(0, n + 1))
        with self.assertRaises(IndexError):
            with self.assertRaises(IndexError):
                np_A[range(-(n + 1), -1)]
            query_table(pa_table, range(-(n + 1), -1))
        with self.assertRaises(IndexError):
            with self.assertRaises(IndexError):
                np_A[range(n, n + 1)]
            query_table(pa_table, range(n, n + 1))

    def test_query_table_str(self):
        pa_table = self._create_dummy_table()
        subtable = query_table(pa_table, "a")
        self.assertTableEqual(subtable, pa.Table.from_pydict({"a": _COL_A}))
        with self.assertRaises(KeyError):
            query_table(pa_table, "z")

    def test_query_table_iterable(self):
        pa_table = self._create_dummy_table()
        n = pa_table.num_rows
        np_A, np_B, np_C = np.array(_COL_A, dtype=np.int64), np.array(_COL_B), np.array(_COL_C)
        # classical usage
        subtable = query_table(pa_table, [0])
        self.assertTableEqual(
            subtable, pa.Table.from_pydict({"a": np_A[[0]], "b": np_B[[0]], "c": np_C[[0]].tolist()})
        )
        subtable = query_table(pa_table, [1])
        self.assertTableEqual(
            subtable, pa.Table.from_pydict({"a": np_A[[1]], "b": np_B[[1]], "c": np_C[[1]].tolist()})
        )
        subtable = query_table(pa_table, [-1])
        self.assertTableEqual(
            subtable, pa.Table.from_pydict({"a": np_A[[-1]], "b": np_B[[-1]], "c": np_C[[-1]].tolist()})
        )
        subtable = query_table(pa_table, [0, -1, 1])
        self.assertTableEqual(
            subtable,
            pa.Table.from_pydict({"a": np_A[[0, -1, 1]], "b": np_B[[0, -1, 1]], "c": np_C[[0, -1, 1]].tolist()}),
        )
        # numpy iterable
        subtable = query_table(pa_table, np.array([0, -1, 1]))
        self.assertTableEqual(
            subtable,
            pa.Table.from_pydict({"a": np_A[[0, -1, 1]], "b": np_B[[0, -1, 1]], "c": np_C[[0, -1, 1]].tolist()}),
        )
        # empty ouput but no errors
        subtable = query_table(pa_table, [])
        assert len(np_A[[]]) == 0
        self.assertTableEqual(subtable, pa.Table.from_batches([], schema=pa_table.schema))
        # raise an IndexError
        with self.assertRaises(IndexError):
            with self.assertRaises(IndexError):
                np_A[[n]]
            query_table(pa_table, [n])
        with self.assertRaises(IndexError):
            with self.assertRaises(IndexError):
                np_A[[-(n + 1)]]
            query_table(pa_table, [-(n + 1)])

    def test_query_table_invalid_key_type(self):
        pa_table = self._create_dummy_table()
        with self.assertRaises(TypeError):
            query_table(pa_table, 0.0)
        with self.assertRaises(TypeError):
            query_table(pa_table, [0, "a"])
        with self.assertRaises(TypeError):
            query_table(pa_table, int)
        with self.assertRaises(TypeError):

            def iter_to_inf(start=0):
                while True:
                    yield start
                    start += 1

            query_table(pa_table, iter_to_inf())
