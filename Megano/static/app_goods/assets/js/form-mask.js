let phone = document.querySelector("input[type='tel']")
var im = new Inputmask("+7 (999) 999-99-99",{'removeMaskOnSubmit':true})
im.mask(phone);
Inputmask.extendDefaults({
  'removeMaskOnSubmit': true
});
new window.JustValidate('.js-form', {
    colorWrong: '#CCB26E',

    rules: {
        name: {
            required: true
        },
        email: {
            required: true,
            email: true
        },
        phone: {
            required: true,
            function: (name, value) => {
                const ph = phone.inputmask.unmaskedvalue();
                return Number(ph) && ph.length === 10;
            }
        },
    },

    messages: {
        email: {
            required: "Не правильно введено поле"
        },
        name: "Не правильно введено поле",
        phone: {
            required: "Не правильно введено поле",
            function: "Не достаточно количество символов"
        }
    }
});
