function getCookie(c_name) {
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) {
                c_end = document.cookie.length;
            }
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
}

function populateMenu(firstName, isSessionValid) {
    if(isSessionValid == 'True') isSessionValid = true
    else isSessionValid = false
    if (isSessionValid) {
    menuHTML  = '<nav class="sidebar">\n'
    menuHTML += '   <header>\n'
    menuHTML += '       <div class="image-text">\n'
    menuHTML += '           <div class="text logo-text">\n'
    menuHTML += '               <a href="home"><span class="name">PurchasePlanner</span></a>\n'
    menuHTML += '           </div>\n'
    menuHTML += '       </div>\n'
    menuHTML += '   </header>\n'
    menuHTML += '   <div class="menu-bar">\n'
    menuHTML += '       <div class="menu">\n'
    menuHTML += '           <ul>\n'
    menuHTML += '               <li><a href="show_files"><span class="text">Show Files</span></a></li>\n'
    menuHTML += '               <li><a href="file_upload"><span class="text">File Upload</span></a></li>\n'
    menuHTML += '               <li><a href="file_data"><span class="text">View Data</span></a></li>\n'
    menuHTML += '               <li><a href="explore"><span class="text">Explore Data</span></a></li>\n'
    menuHTML += '               <li><a href="visualize"><span class="text">Visualize Data</span></a></li>\n'
    menuHTML += '               <li><a href="stationary"><span class="text">Data Stationary Test</span></a></li>\n'
    menuHTML += '               <li><a href="model_test"><span class="text">ARIMA Model Test</span></a></li>\n'
    menuHTML += '               <li><a href="product_demand"><span class="text">Estimate Demand</span></a></li>\n'
    menuHTML += '           </ul>\n'
    menuHTML += '       </div>\n'
    menuHTML += '       <div class="bottom-content">\n'
    menuHTML += '           <hr />\n'
    menuHTML += '           <span class="title">'+firstName.charAt(0).toUpperCase() + firstName.slice(1)+'</span>\n'
    menuHTML += '           <ul>\n'
    menuHTML += '               <li><a href="update_profile"><span class="text">Update Profile</span></a></li>\n'
    menuHTML += '               <li><a href="change_password"><span class="text">Change Password</span></a></li>\n'
    menuHTML += '               <li><a href="logout"><span class="text">Logout</span></a></li>\n'
    menuHTML += '           </ul>\n'
    menuHTML += '       </div>\n'
    menuHTML += '   </div>\n'
    menuHTML += '</nav>\n'
    } else {
    menuHTML  = '<nav class="horizontal_menu">\n'
    menuHTML += '   <div class="nav-bar">\n'
    menuHTML += '      <header>\n'
    menuHTML += '          <div class="image-text">\n'
    menuHTML += '              <div class="text logo-text">\n'
    menuHTML += '                  <a href="home"><span class="name">PurchasePlanner</span></a>\n'
    menuHTML += '              </div>\n'
    menuHTML += '          </div>\n'
    menuHTML += '      </header>\n'
    menuHTML += '      <div class="darkLight-searchBox">\n'
    menuHTML += '          <div class="dark-light">\n'
    menuHTML += '              <a href="signup">Signup</a>/<a href="login">Login</a>\n'
    menuHTML += '          </div>\n'
    menuHTML += '      </div>\n'
    menuHTML += '   </div>\n'
    menuHTML += '</nav>\n'
    }
    document.getElementById('menu').innerHTML = menuHTML
}

function setInnerHTML() {
    var firstName = getCookie('first_name')
    var isSessionValid = getCookie('is_valid_session')
    populateMenu(firstName, isSessionValid)
}