@echo off
setlocal

cd %~dp0

call ..\setup_vs_tools.cmd
if not %ERRORLEVEL%==0 (exit /b 1)

msbuild /nologo /v:m /m /p:Configuration=Release /p:OutputPath=pub
if not %ERRORLEVEL%==0 (goto :notok)

:ok
echo assembled ok
exit /b 0

:notok
echo failed to assemble
exit /b 1