

# CRITIAL ERROR #1
the goal is to simplify  (but not make it fully generic like spec kit)
you cant just make it simple without features:
becuase this is a complete failure - otherwise why would i not just use spec-kit https://github.com/github/spec-kit
(its fine but it exists)

# CRITICAL ERROR #2
it must have the rigor + logging rules in it ! no execptions (vibe or spec) if you dont you fail 100%

# CRITICAL ERROR #3
i must have my /flow:submit-n-reivew-pr as thats a CRITICAL STEP that you cant remove (if you did you fucked up)
why not use it on your own REALLY BAD AND NOW CLOSED PR https://github.com/jpoley/flowspec/pull/1061

# CRITICAL ERROR #4
failed checks in security (not ok)
Code scanning/ Semgrep
(critical )
bash.curl.security.curl-pipe-bash.curl-pipe-bashWarning

Detected the use of eval(). eval() can be dangerous if used to evaluate dynamic content. If this content can be input from outside the program, this may be a code injection vulnerability. Ensure evaluated content is not definable by external sources.

# CRITCAL ERROR # 5

BAD CICD

see @docs/ouch.png
you can't ever fail any CICD checks (ever) it means your PR is a failure

# CRITICAL ERROR # 6
using bash to call task commands, use MCP - this is not correct.

