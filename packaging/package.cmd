@echo off
pushd %~dp0
pyinstaller -F -y ..\startup.pyw
xcopy /I /E /Y ..\resources .\dist\resources
popd