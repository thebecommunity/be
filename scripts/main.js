// This gives the offset that Kata.include needs prepended
// to get to the base of our code directory (it starts at
// katajs.git, so we need to get out of externals/katajs.git).
var kata_base_offset = "../../";

var kata, graphics;
var driver = "GLGE";
var loginName = null;
var avatarURL = null;
var avatarScale = null;

function handleLogin(name, avatar) {
    loginName = name;
    avatarURL = avatar.url;
    avatarScale = avatar.scale;
    
    Kata.require([
                    // Post login
                     'katajs/oh/MainThread.js',
                     'katajs/space/loop/Space.js',
                     'katajs/oh/GraphicsSimulation.js',
                     'katajs/gfx/glgegfx.js',
                     'katajs/oh/Script.js',
                     'katajs/oh/plugins/loop/LoopbackSpaceConnection.js',
                     'katajs/oh/plugins/sirikata/SirikataSpaceConnection.js',
                     'katajs/oh/ObjectHost.js',
                     kata_base_offset + 'scripts/ui/chat.js',
                     kata_base_offset + 'scripts/ui/session.js',
                     kata_base_offset + 'scripts/ui/toolbar.js',
                     kata_base_offset + 'scripts/ui/sit.js',
                     kata_base_offset + 'scripts/ui/help.js'
                 ], function() {
                     loadGFX();
                 });
}

function onDocReady() {
    $('#container').hide();
    
    var have_deps = true;
    if (!Modernizr.webgl) {
        $.jnotify("Your browser doesn't support WebGL.", 'error', true);
        have_deps = false;
    }
    if (!Modernizr.websockets) {
        $.jnotify("Your browser doesn't support WebSockets.", 'error', true);
        have_deps = false;
    }
    if (!Modernizr.webworkers) {
        $.jnotify("Your browser doesn't support WebWorkers.", 'error', true);
        have_deps = false;
    }
    
    if (!have_deps) {
        $.jnotify("Currently we recommend the latest <a href=\"http://www.google.com/landing/chrome/beta/\">Chrome Beta</a> for all platforms.<br>In recent Firefox Betas you may need to explicitly enable these features via the about:config page.", 'error', true);
        return;
    }
    
    Kata.require([
                    // Pre login
                     kata_base_offset + 'scripts/ui/antiscroll.js',
                     kata_base_offset + 'scripts/ui/login.js',
                     kata_base_offset + 'scripts/ui/footer.js'
                 ], function() {
                     antiScroll();
                     loginui = new LoginUI( $("#login"), Avatars, handleLogin);
                     
                     $('#title').append(Title);
                     
                     footerui = new FooterUI(
                         $(FooterContent())
                     );
                 });
}

function loadGFX(){
    $('#container').show();
    
    toolbar = new ToolbarUI($('#container'));
    
    function graphicsReady () {
        window.kata = new Kata.MainThread(
            kata_base_offset + "scripts/BlessedScript.js",
            "Example.BlessedScript",
            {
                space: SpaceURL,
                name: loginName,
                scale : avatarScale,
                visual: {mesh: avatarURL}
            });
        graphics = new Kata.GraphicsSimulation(driver, window.kata.getChannel(), document.getElementById("container"));
        session = new SessionUI(window.kata.getChannel());
        situi = new SitUI(window.kata.getChannel(), toolbar);
        helpui = new HelpUI(window.kata.getChannel(), toolbar);
        chats = new ChatUI(window.kata.getChannel(), loginName, 300);
        chats.create("Chat");
    }
    
    Kata.GraphicsSimulation.initializeDriver(driver, "static/glge_level.xml", graphicsReady);
}

window.onload = onDocReady;