# Home Sweet Home
This is a tool designed for anyone tired of messing with tmux configurations, having conflicting configurations depending on the use case, have to manually manage they projects, etc ...

HSH will automate configurations loading on any software (who supports the redirection with a particular config file),
will create project directory (git repo, direnv, README, aliases) and will manage them (create, delete, backup, restore, etc ...)

(Project in development, but feel free to do anything you want with it)

TODO:
    - Change tmux default command on new pane to the script thing
    - Create archive of past log files when opening project and store them in compressed archive
    tmux set -g default-command "script -f /tmp/testlogtmuxpane -c 'bash -i'"
