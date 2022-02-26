$(document).ready(function(){
    const persian_numbers = {
            1: 'یک',
            2: 'دو',
            3: 'سه',
            4: 'چهار',
            5: 'پنج', 
            6: 'شش',
            7: 'هفت',
            8: 'هشت',
            9: 'نه',
            10: 'ده',
            11: 'یازده',
            12: 'دوازده'
        };

    

    $('#wordAugment').on('click', function(event){
        addWord(event);
    });

    $('form').submit((event)=>{
        console.log($('#word'+(0+1)).val())
        const words = document.getElementById('words');
        let words_number = words.children.length;
        
        let words_list = [] 
        console.log(words_number)
        for(let i = 0; i < words_number; i++){
            let word = $('#word'+(i+1)).val()
            console.log(i)
            if(word != null && word != '')
                words_list.push(word)
        }
        

        let  formData = {
            'sentence': $('#sentence').val(),
            'words': words_list
        }
        event.preventDefault();
        console.log(formData);
        sendData(formData, 'http://127.0.0.1:5000/')
        // console.log(response)
        // if(response != null){
        //     addResult(response)
        // }
        event.preventDefault();
        // call send data with ajax
    });

    function sendData(formData, url){
        
        $.ajax({
            type: 'post',
            url: url,
            contentType: "application/json",
            data: JSON.stringify(formData),
            success: function(data){
                serverResponse = data['modelResponse'];
                console.log(serverResponse);
                addResult(serverResponse)
            },
            error: function(data){
                document.getElementById('error_messages').innerHTML = "<div class='alert alert-danger'>خطایی در سمت سرور پیش آمده است، لطفا با ادمین تماس بگیرید.</div>";
                console.log(data);
            }
        }).done(function(data) {
            console.log(data);
        });
    }

    function addWord(event){
        const words = document.getElementById('words');
        let words_number = words.children.length;
        if(words_number > 12){
            document.getElementById('error_messages').innerHTML = "<div class='alert alert-danger'>بیشتر از این دیگر نمی‌توانید کلمه اضافه کنید.</div>";
            event.preventDefault();
            return;   
        }
        let persian_num = persian_numbers[words_number+1]
        let new_word_form = `<div class="form-group">
                <input type="text" class="form-control" id="word${words_number+1}" name="word${words_number+1}" placeholder="کلمه ${persian_num}">
                <label class="__label" for="word${words_number+1}">کلمه ${persian_num}</label>
            </div>`;
        console.log(new_word_form);
        words.innerHTML += new_word_form;
        event.preventDefault();
    }

    function addResult(response){
        console.log(response)
        const results = document.getElementById('results');
        results.innerHTML = '';
        for(let i = response.length-1; i > -1; i--){
            results.innerHTML += `<div class="wordScore"><span class="word">${response[i][0]}</span> <i class="fa-solid fa-arrow-left-long"></i> <span class="score">${response[i][1].toPrecision(2)}</span></div>`
        }
    }
});