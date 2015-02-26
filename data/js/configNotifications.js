$(document).ready(function () {
    var loading = '<img src="' + sbRoot + '/images/loading16.gif" height="16" width="16" />';

    $('#testGrowl').click(function () {
        $('#testGrowl-result').html(loading);
        var growl_host = $("#growl_host").val();
        var growl_password = $("#growl_password").val();
        $.get(sbRoot + "/home/testGrowl", {'host': growl_host, 'password': growl_password},
            function (data) { $('#testGrowl-result').html(data); });
    });

    $('#testProwl').click(function () {
        $('#testProwl-result').html(loading);
        var prowl_api = $("#prowl_api").val();
        var prowl_priority = $("#prowl_priority").val();
        $.get(sbRoot + "/home/testProwl", {'prowl_api': prowl_api, 'prowl_priority': prowl_priority},
            function (data) { $('#testProwl-result').html(data); });
    });

    $('#testXBMC').click(function () {
        $("#testXBMC").attr("disabled", true);
        $('#testXBMC-result').html(loading);
        var xbmc_host = $("#xbmc_host").val();
        var xbmc_username = $("#xbmc_username").val();
        var xbmc_password = $("#xbmc_password").val();
		
        $.get(sbRoot + "/home/testXBMC", {'host': xbmc_host, 'username': xbmc_username, 'password': xbmc_password})
            .done(function (data) {
                $('#testXBMC-result').html(data);
                $("#testXBMC").attr("disabled", false);
            });
    });

    $('#testPLEX').click(function () {
        $('#testPLEX-result').html(loading);
        var plex_host = $("#plex_host").val();
        var plex_username = $("#plex_username").val();
        var plex_password = $("#plex_password").val();
        $.get(sbRoot + "/home/testPLEX", {'host': plex_host, 'username': plex_username, 'password': plex_password},
            function (data) { $('#testPLEX-result').html(data); });
    });

    $('#testBoxcar').click(function () {
        $('#testBoxcar-result').html(loading);
        var boxcar_username = $("#boxcar_username").val();
        $.get(sbRoot + "/home/testBoxcar", {'username': boxcar_username},
            function (data) { $('#testBoxcar-result').html(data); });
    });

    $("#testBoxcar2").click(function () {
        var boxcar2_access_token = $.trim($("#boxcar2_access_token").val());
        var boxcar2_sound = $("#boxcar2_sound").val() || "default";
        if (!boxcar2_access_token) {
            $("#testBoxcar2-result").html("Please fill out the necessary fields above.");
            return;
        }
        $(this).prop("disabled", true);
        $("#testBoxcar2-result").html(loading);
        $.get(sbRoot + "/home/testBoxcar2", {'accessToken': boxcar2_access_token, 'sound': boxcar2_sound})
            .done(function (data) {
                $("#testBoxcar2-result").html(data);
                $("#testBoxcar2").prop("disabled", false);
            });
    });

    $('#testPushover').click(function () {
        $('#testPushover-result').html(loading);
        var pushover_userkey = $("#pushover_userkey").val();
        $.get(sbRoot + "/home/testPushover", {'userKey': pushover_userkey},
            function (data) { $('#testPushover-result').html(data); });
    });

    $('#testLibnotify').click(function () {
        $('#testLibnotify-result').html(loading);
        $.get(sbRoot + "/home/testLibnotify",
            function (data) { $('#testLibnotify-result').html(data); });
    });

    $('#twitterStep1').click(function () {
        $('#testTwitter-result').html(loading);
        $.get(sbRoot + "/home/twitterStep1", function (data) {window.open(data); })
            .done(function () { $('#testTwitter-result').html('<b>Step1:</b> Confirm Authorization'); });
    });

    $('#twitterStep2').click(function () {
        $('#testTwitter-result').html(loading);
        var twitter_key = $("#twitter_key").val();
        $.get(sbRoot + "/home/twitterStep2", {'key': twitter_key},
            function (data) { $('#testTwitter-result').html(data); });
    });

    $('#testTwitter').click(function () {
        $.get(sbRoot + "/home/testTwitter",
            function (data) { $('#testTwitter-result').html(data); });
    });

    $('#settingsNMJ').click(function () {
        if (!$('#nmj_host').val()) {
            alert('Please fill in the Popcorn IP address');
            $('#nmj_host').focus();
            return;
        }
        $('#testNMJ-result').html(loading);
        var nmj_host = $('#nmj_host').val();

        $.get(sbRoot + "/home/settingsNMJ", {'host': nmj_host},
            function (data) {
                if (data === null) {
                    $('#nmj_database').removeAttr('readonly');
                    $('#nmj_mount').removeAttr('readonly');
                }
                var JSONData = $.parseJSON(data);
                $('#testNMJ-result').html(JSONData.message);
                $('#nmj_database').val(JSONData.database);
                $('#nmj_mount').val(JSONData.mount);

                if (JSONData.database) {
                    $('#nmj_database').attr('readonly', true);
                } else {
                    $('#nmj_database').removeAttr('readonly');
                }
                if (JSONData.mount) {
                    $('#nmj_mount').attr('readonly', true);
                } else {
                    $('#nmj_mount').removeAttr('readonly');
                }
            });
    });

    $('#testNMJ').click(function () {
        $('#testNMJ-result').html(loading);
        var nmj_host = $("#nmj_host").val();
        var nmj_database = $("#nmj_database").val();
        var nmj_mount = $("#nmj_mount").val();

        $.get(sbRoot + "/home/testNMJ", {'host': nmj_host, 'database': nmj_database, 'mount': nmj_mount},
            function (data) { $('#testNMJ-result').html(data); });
    });

    $('#settingsNMJv2').click(function () {
        if (!$('#nmjv2_host').val()) {
            alert('Please fill in the Popcorn IP address');
            $('#nmjv2_host').focus();
            return;
        }
        $('#testNMJv2-result').html(loading);
        var nmjv2_host = $('#nmjv2_host').val();
        var nmjv2_dbloc;
        var radios = document.getElementsByName("nmjv2_dbloc");
        for (var i = 0; i < radios.length; i++) {
            if (radios[i].checked) {
                nmjv2_dbloc=radios[i].value;
                break;
            }
        }

        var nmjv2_dbinstance=$('#NMJv2db_instance').val();
        $.get(sbRoot + "/home/settingsNMJv2", {'host': nmjv2_host, 'dbloc': nmjv2_dbloc, 'instance': nmjv2_dbinstance},
        function (data){
            if (data == null) {
                $('#nmjv2_database').removeAttr('readonly');
            }
            var JSONData = $.parseJSON(data);
            $('#testNMJv2-result').html(JSONData.message);
            $('#nmjv2_database').val(JSONData.database);
            
            if (JSONData.database) {
                $('#nmjv2_database').attr('readonly', true);
            } else {
                $('#nmjv2_database').removeAttr('readonly');
            }
        });
    });

    $('#testNMJv2').click(function () {
        $('#testNMJv2-result').html(loading);
        var nmjv2_host = $("#nmjv2_host").val();
        
        $.get(sbRoot + "/home/testNMJv2", {'host': nmjv2_host},
            function (data){ $('#testNMJv2-result').html(data); });
    });

    $('#testTrakt').click(function () {
        $('#testTrakt-result').html(loading);
        var trakt_api = $("#trakt_api").val();
        var trakt_username = $("#trakt_username").val();
        var trakt_password = $("#trakt_password").val();

        $.get(sbRoot + "/home/testTrakt", {'api': trakt_api, 'username': trakt_username, 'password': trakt_password},
            function (data) { $('#testTrakt-result').html(data); });
    });

    $('#testNMA').click(function () {
        $('#testNMA-result').html(loading);
        var nma_api = $("#nma_api").val();
        var nma_priority = $("#nma_priority").val();
        $.get(sbRoot + "/home/testNMA", {'nma_api': nma_api, 'nma_priority': nma_priority},
            function (data) { $('#testNMA-result').html(data); });
    });
    
    $('#testMail').click(function () {
        $('#testMail-result').html(loading);
        var mail_from = $("#mail_from").val();
        var mail_to = $("#mail_to").val();
        var mail_server = $("#mail_server").val();
        var mail_ssl = $("#mail_ssl").val();
        var mail_username = $("#mail_username").val();
        var mail_password = $("#mail_password").val();
           
        $.get(sbRoot + "/home/testMail", {},
            function (data) { $('#testMail-result').html(data); });
    });
    
     $('#testPushalot').click(function () {
        $('#testPushalot-result').html(loading);
        var pushalot_authorizationtoken = $("pushalot_authorizationtoken").val();
        $.get(sbRoot + "/home/testPushalot", {'authorizationToken': pushalot_authorizationtoken},
            function (data) { $('#testPushalot-result').html(data); });
    });
    
    $('#testPushbullet').click(function () {
        $('#testPushbullet-result').html(loading);
        var pushbullet_api = $("#pushbullet_api").val();
        if($("#pushbullet_api").val() == '') {
            $('#testPushbullet-result').html("You didn't supply a Pushbullet api key");
            $("#pushbullet_api").focus();
            return false;
        }
        $.get(sbRoot + "/home/testPushbullet", {'api': pushbullet_api},
            function (data) {
                $('#testPushbullet-result').html(data);
            }
        );
    });

    function get_pushbullet_devices(msg){

        if(msg){
            $('#testPushbullet-result').html(loading);
        }
        
        var pushbullet_api = $("#pushbullet_api").val();

        if(!pushbullet_api) {
            $('#testPushbullet-result').html("You didn't supply a Pushbullet api key");
            $("#pushbullet_api").focus();
            return false;
        }
        $("#pushbullet_device_list").html('');
        var current_pushbullet_device = $("#pushbullet_device").val();
        $.get(sbRoot + "/home/getPushbulletDevices", {'api': pushbullet_api},
            function (data) {
                var devices = jQuery.parseJSON(data).devices;
                
                for (var i = 0; i < devices.length; i++) {
                    if(devices[i].active == true && devices[i].pushable == true){
                        if(current_pushbullet_device ==  'device:'+devices[i].iden) {
                            $("#pushbullet_device_list").append('<option value="device:'+devices[i].iden+'" selected>' + devices[i].nickname + '</option>')
                        } else {
                            $("#pushbullet_device_list").append('<option value="device:'+devices[i].iden+'">' + devices[i].nickname + '</option>')
                        }
                    }
                }
                if(msg) {
                    $('#testPushbullet-result').html(msg);
                }
            }
        );

        $.get(sbRoot + "/home/getPushbulletChannels", {'api': pushbullet_api},
            function (data) {
                var channels = jQuery.parseJSON(data).channels;

                for (var i = 0; i < channels.length; i++) {
                    if(channels[i].active == true){
                        if(current_pushbullet_device == 'channel:'+channels[i].tag) {
                            $("#pushbullet_device_list").append('<option value="channel:'+channels[i].tag+'" selected>' + channels[i].name + '</option>')
                        } else {
                            $("#pushbullet_device_list").append('<option value="channel:'+channels[i].tag+'">' + channels[i].name + '</option>')
                        }
                    }
                }
                if(msg) {
                    $('#testPushbullet-result').html(msg);
                }
            }
        );

        $("#pushbullet_device_list").change(function(){
            $("#pushbullet_device").val($("#pushbullet_device_list").val());
            $('#testPushbullet-result').html("Don't forget to save your new pushbullet settings.");
        });
    };

    $('#getPushbulletDevices').click(function(){
        get_pushbullet_devices("Device list updated. Please choose a device to push to.");
    });
    
    // we have to call this function on dom ready to create the devices select
    get_pushbullet_devices();
	
    $('#testBetaSeries').click(function () {
        $('#testBetaSeries-result').html(loading);
        var betaseries_username = $("#betaseries_username").val();
        var betaseries_password = $("#betaseries_password").val();

        $.get(sbRoot + "/home/testBetaSeries", {'username': betaseries_username, 'password': betaseries_password},
            function (data) { $('#testBetaSeries-result').html(data); });
    });

    $('#email_show').change(function () {
        var key = parseInt($('#email_show').val(), 10);
        $('#email_show_list').val(key >= 0 ? notify_data[key.toString()].list : '');
	});

    // Update the internal data struct anytime settings are saved to the server
    $('#email_show').bind('notify', function () { load_show_notify_lists(); });

    function load_show_notify_lists() {
        $.get(sbRoot + "/home/loadShowNotifyLists", function (data) {
            var list, html, s;
            list = $.parseJSON(data);
            notify_data = list;
            if (list._size === 0) {
                return;
            }
            html = '<option value="-1">-- Select --</option>';
            for (s in list) {
                if (s.charAt(0) !== '_') {
                    html += '<option value="' + list[s].id + '">' + $('<div/>').text(list[s].name).html() + '</option>';
                }
            }
            $('#email_show').html(html);
            $('#email_show_list').val('');
        });
    }
    // Load the per show notify lists everytime this page is loaded
    load_show_notify_lists();
});
