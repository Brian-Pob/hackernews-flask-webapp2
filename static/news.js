// let like_buttons = document.getElementsByClassName("like-button");

// for(let i = 0; i < like_buttons.length; i ++){
//     like_buttons[i].addEventListener("click",(e) => {
//         let class_list = e.target.classList
//         if(class_list.contains("fa-regular")){
//             e.target.classList.remove("fa-regular")
//             e.target.classList.add("fa-solid")
//         }
//         else{
//             e.target.classList.remove("fa-solid")
//             e.target.classList.add("fa-regular")
//         }
//     })
// }

let titles = document.getElementsByClassName("post-title")

for(let i = 0; i < titles.length; i ++){
    titles[i].addEventListener("mouseenter", (e) => {
        let class_list = e.target.classList

        if(class_list.contains("title-default")){
            e.target.classList.remove("title-default")
            e.target.classList.add("title-onclick")

            fetch('/preview')
                .then((response) => response.json())
                .then((data) => console.log(data));
        
        }
    })
    titles[i].addEventListener("mouseleave", (e) => {
        let class_list = e.target.classList
        if(class_list.contains("title-onclick")){
            e.target.classList.remove("title-onclick")
            e.target.classList.add("title-default")
        }
    })
}

let article_blocks = document.getElementsByClassName("news-post-default")

for(let i = 0; i < article_blocks.length; i ++){
    article_blocks[i].addEventListener("mouseenter", (e) => {
        let class_list = e.target.classList

        if(class_list.contains("news-post-default")){
            e.target.classList.remove("news-post-default")
            e.target.classList.add("news-post-onfocus")
            console.log(`/preview?url=${e.target.getAttribute("data-url")}`)
            e.target.getElementsByClassName("web-preview")[0].classList.remove("web-preview-hidden")
            e.target.getElementsByClassName("web-preview")[0].classList.add("web-preview-visible")
            e.target.getElementsByClassName("web-preview")[0].innerHTML = "Loading preview..."
            fetch(`/preview?url=${e.target.getAttribute("data-url")}`)
                .then((response) => response.json())
                .then((data) => {
                    e.target.getElementsByClassName("web-preview")[0].innerHTML = data.description
                });
        }
    })

    article_blocks[i].addEventListener("mouseleave", (e) => {
        let class_list = e.target.classList

        if(class_list.contains("news-post-onfocus")){
            e.target.classList.remove("news-post-onfocus")
            e.target.classList.add("news-post-default")
            e.target.getElementsByClassName("web-preview")[0].classList.remove("web-preview-visible")
            e.target.getElementsByClassName("web-preview")[0].classList.add("web-preview-hidden")
            e.target.getElementsByClassName("web-preview")[0]
        }
    })
}