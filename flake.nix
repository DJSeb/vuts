{
  description = "AI in workflow flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    system = "x86_64-linux";
    pkgs = import nixpkgs {
      inherit system;
      config.allowUnfree = true;
    };
    vscode-with-extensions = pkgs.vscode-with-extensions.override {
      vscode = pkgs.vscode;
      vscodeExtensions = with pkgs.vscode-extensions; [
        ms-python.python
        ms-python.pylint
        ms-python.debugpy
        github.copilot
        github.copilot-chat
      ];
    };
    git-confd = pkgs.git.override {
      
    };
    fhs-env = pkgs.buildFHSEnv {
      name = "data-sci-env";
      targetPkgs = pkgs:
        with pkgs;
          [
            tree
            git
            git-lfs
            python313
            gcc
            libgcc
            libz
          ] ++ [vscode-with-extensions];

      profile = ''
        alias ez="eza"
        alias ezl="eza -l"
        alias ezlA="eza -lA"
        export PS1="\e[1;90m𜸖'AI in workflow', \s-$SHLVL𜸘\e[0m \033[38;5;196m$?\033[0m\n\[\e[0;32m\][\[\e[1;32m\]\u@\h\[\e[0;32m\]]\[\e[0m\] \[\e[1;90m\]\w\[\e[0m\]\n \-> "

        git config --global user.name "David Jaromír Šebánek"
        git config --global user.email "djsebofficial@gmail.com"
      '';

      runScript = "bash --rcfile /etc/profile -i";
    };
  in {
    devShells.${system}.default = fhs-env.env;
  };
}
