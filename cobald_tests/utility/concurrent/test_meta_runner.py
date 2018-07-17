import threading
import pytest
import time
import asyncio

import trio

from cobald.utility.concurrent.base_runner import OrphanedReturn
from cobald.utility.concurrent.meta_runner import MetaRunner


class TerminateRunner(Exception):
    pass


def run_in_thread(payload, name, daemon=True):
    thread = threading.Thread(target=payload, name=name, daemon=daemon)
    thread.start()


class TestMetaRunner(object):
    def test_run_subroutine(self):
        """Test executing a subroutine"""
        def with_return():
            return 'expected return value'

        for flavour in (threading,):
            runner = MetaRunner()
            result = runner.run_payload(with_return, flavour=flavour)
            assert result == with_return()

    def test_run_coroutine(self):
        """Test executing a subroutine"""
        async def with_return():
            return 'expected return value'

        for flavour in (trio,):
            runner = MetaRunner()
            run_in_thread(runner.run, name='test_run_coroutine')
            result = runner.run_payload(with_return, flavour=flavour)
            # TODO: can we actually get the value from with_return?
            assert result == 'expected return value'
            runner.stop()

    def test_return_subroutine(self):
        """Test that returning from subroutines aborts runners"""
        def with_return():
            return 'unhandled return value'

        for flavour in (threading,):
            runner = MetaRunner()
            runner.register_payload(with_return, flavour=flavour)
            with pytest.raises(RuntimeError) as exc:
                runner.run()
            assert isinstance(exc.value.__cause__, OrphanedReturn)

    def test_return_coroutine(self):
        """Test that returning from subroutines aborts runners"""
        async def with_return():
            return 'unhandled return value'

        for flavour in (asyncio, trio):
            runner = MetaRunner()
            runner.register_payload(with_return, flavour=flavour)
            with pytest.raises(RuntimeError) as exc:
                runner.run()
            assert isinstance(exc.value.__cause__, OrphanedReturn)

    def test_abort_subroutine(self):
        """Test that failing subroutines abort runners"""
        def abort():
            raise TerminateRunner

        for flavour in (threading,):
            runner = MetaRunner()
            runner.register_payload(abort, flavour=flavour)
            with pytest.raises(RuntimeError) as exc:
                runner.run()
            assert isinstance(exc.value.__cause__, TerminateRunner)

            def noop():
                return

            def loop():
                while True:
                    time.sleep(0)

            runner = MetaRunner()
            runner.register_payload(noop, loop, flavour=flavour)
            runner.register_payload(abort, flavour=flavour)
            with pytest.raises(RuntimeError) as exc:
                runner.run()
            assert isinstance(exc.value.__cause__, TerminateRunner)

    def test_abort_coroutine(self):
        """Test that failing coroutines abort runners"""
        async def abort():
            raise TerminateRunner

        for flavour in (asyncio, trio):
            runner = MetaRunner()
            runner.register_payload(abort, flavour=flavour)
            with pytest.raises(RuntimeError) as exc:
                runner.run()
            assert isinstance(exc.value.__cause__, TerminateRunner)

            async def noop():
                return

            async def loop():
                while True:
                    await flavour.sleep(0)
            runner = MetaRunner()

            runner.register_payload(noop, loop, flavour=flavour)
            runner.register_payload(abort, flavour=flavour)
            with pytest.raises(RuntimeError) as exc:
                runner.run()
            assert isinstance(exc.value.__cause__, TerminateRunner)
