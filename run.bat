@echo off
for /f "tokens=*" %%s in (.env) do (
  call set %%s
)

if "--make-migrations" == "%1%" (
    goto :make_migrations
)
if "-mm" == "%1%" (
    goto :make_migrations
) else (
    goto :starting
)

:make_migrations
echo make migrations
start /wait "" migrations\make_all
goto :starting

:starting
echo starting
start python tgbot\main.py