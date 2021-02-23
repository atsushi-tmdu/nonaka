
wnload pyenv
git clone https://github.com/yyuu/pyenv.git ~/.pyenv
​
# For pyenv
echo "# For pyenv" > ~/.bash_profile
echo "export PYENV_ROOT=\$HOME/.pyenv" >> ~/.bash_profile
echo "export PATH=\$PYENV_ROOT/bin:\$PATH" >> ~/.bash_profile
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
​
# Activate pyenv
source ~/.bash_profile
​
# Install python 3.6.8
pyenv install 3.6.8
​
# Download virtualenv
git clone https://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
​
# For virtualenv
echo "# For virtualenv" >> ~/.bash_profile
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bash_profile
​
# Activate virtualenv
source ~/.bash_profile
​
# Create virtualenv environment
pyenv virtualenv 3.6.8 env_base
​
# Globally apply new env
pyenv global env_base
