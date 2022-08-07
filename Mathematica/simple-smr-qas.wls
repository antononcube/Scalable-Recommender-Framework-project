#!/usr/local/bin/wolframscript -args
(* Too simple, but just an example. It is better to NLP Template Engine.*)
argv = Rest @ $ScriptCommandLine;
argc = Length @ argv;
command = StringRiffle[argv, " "];
smrType = FindTextualAnswer[command, "With what"];
nrecs = FindTextualAnswer[command, "How many"];
command2 = StringReplace[command, {smrType -> "", nrecs -> ""}];
query = FindTextualAnswer[command, "Which profile"];
Print[" --nrecs " <> nrecs <> " --smr " <> smrType <> " " <> query];