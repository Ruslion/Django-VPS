// insert your block id
const AdController = window.Adsgram.init({ blockId: "3755", 
    debug: true,
    debugBannerType: "FullscreenMedia"  });
const button = document.getElementById('ad');
button.addEventListener('click', () => {
        AdController.show().then((result) => {
            // user watch ad till the end
            // your code to reward user
        }).catch((result) => {
            // user skipped video or get error during playing ad
            // do nothing or whatever you want
            alert(JSON.stringify(result, null, 4));
        })
})