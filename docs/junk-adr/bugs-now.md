# Code scanning/ Semgrep
(critical )
bash.curl.security.curl-pipe-bash.curl-pipe-bashWarning

Detected the use of eval(). eval() can be dangerous if used to evaluate dynamic content. If this content can be input from outside the program, this may be a code injection vulnerability. Ensure evaluated content is not definable by external sources.


# BAD CICD

see @docs/ouch.png

you can't ever fail any CICD checks (ever) it means your PR is a