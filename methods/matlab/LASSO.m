% @file lasso.m
%
% lasso with matlab.

function lasso(cmd)
% This program trains the lasso on the given dataset
%
% Required options:
%     (-T) [string]    A file containing the Y set.
%     (-t) [string]    A file containing the X set.

x = regexp(cmd, '.*?-t ([^\s]+)', 'tokens', 'once');
y = regexp(cmd, '.*?-T ([^\s]+)', 'tokens', 'once');

% Load input dataset.
X = csvread(x{:});
Y = csvread(y{:});

% Create and train lasso
total_time = tic;
classifier = lasso(X, Y);

disp(sprintf('[INFO ]   total_time: %fs', toc(total_time)))

end
