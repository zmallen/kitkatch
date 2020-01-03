import os
import pytest
from kitkatch import collect
import random


@pytest.fixture
def random_compressed_file():
    return

@pytest.fixture
def html_opendir():
    return '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
 <head>
  <title>Index of /</title>
 </head>
 <body>
<h1>Index of /</h1>
<ul><li><a href="flibflab"> flibflab</a></li>
</ul>
</body></html>
'''

@pytest.fixture
def html_simple():
    return '''
    <html>
    <title>CALL ME RUDE BOY BOY BOY</title>
    </html>
    '''

@pytest.fixture
def html_form():
    return '''
<html>
<head>
<title>Login Page</title>
</head>
<body>
<form name="loginForm" method="post" action="login.php">
<table width="20%" bgcolor="0099CC" align="center">

<tr>
<td colspan=2><center><font size=4><b>Paypal Login</b></font></center></td>
</tr>

<tr>
<td>Username:</td>
<td><input type="text" size=25 name="userid"></td>
</tr>

<tr>
<td>Password:</td>
<td><input type="Password" size=25 name="pwd"></td>
</tr>

<tr>
<td ><input type="Reset"></td>
<td><input type="submit" onclick="return check(this.form)" value="Login"></td>
</tr>

</table>
</form>
<script language="javascript">
function check(form)
{

if(form.userid.value == "admin" && form.pwd.value == "password")
{
	return true;
}
else
{
	alert("Error Password or Username")
	return false;
}
}
</script>

</body>
</html>
'''

def test_collect_file_list():
    KNOWN_EXTENSIONS = [
        'zip',
        'rar',
        '7z',
        'tar',
        'gz'
    ]
    assert(set(KNOWN_EXTENSIONS) == set(collect.compressed_file_list()))

def test_compressed_file_url():
    assert(collect.compressed_file_in_url('https://listenhere.com/bazbar/foo/kit.zip'))

def test_collect_indexed_links_no_open_dir(html_simple):
    assert(collect.collect_indexed_links(html_simple, 'https://foobar.com') == [])


def test_collect_indexed_links_open_dir(html_opendir):
    links = collect.collect_indexed_links(html_opendir, 'https://foobar.com/')
    assert(len(links) == 1)
    assert(links[0] == 'https://foobar.com/flibflab')

def test_build_url_from_parse():
    scheme = 'http'
    netloc = 'foobarbaz.com'
    path = '/sup/my/dude'
    url = collect.build_url_from_parse(scheme, netloc, path)
    assert(url == 'http://foobarbaz.com/sup/my/dude/')
    path = '/sup/my/dude/'
    url = collect.build_url_from_parse(scheme, netloc, path)
    assert(url == 'http://foobarbaz.com/sup/my/dude/')

def test_url_candidates():
    url = 'https://ivan-the-impaler-phishman.000webhostapp.com/com-login-verify/your/account/amazon/signin.php'
    candidates = collect.url_candidates(url)
    assert(len(candidates) == 6)
    url = 'https://ivan-the-impaler-phishman.000webhostapp.com/com-login-verify/'
    candidates = collect.url_candidates(url)
    print(candidates)
    assert(len(candidates) == 2)

def test_get_forms(html_form):
    assert(len(collect.get_forms(html_form)) > 0)
