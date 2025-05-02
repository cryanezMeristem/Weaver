$(document).ready(function(){
    /* recipe label */
    var componentValues = $('.recipe-component-value');
    $('#recipe-concentration').change(function(){
        var recipeConcentration = parseFloat($(this).val());
        if (recipeConcentration <= 0) {
            recipeConcentration = 1;
        }
        $(this).val(recipeConcentration);
        if (recipeConcentration != 1){
            $('#label-name').html(recipeConcentration + "X " + $('#label-name').attr('data-initval'));
        } else{
            $('#label-name').html($('#label-name').attr('data-initval'));
        }
        componentValues.each(function(index){
            $(this).html($(this).attr('data-initval') * recipeConcentration);
        });
    });
    /* select2 */
    $('#id_components, #id_reactive, #id_optional_components').select2();
    /* recipes */
    $('form#prepare input#id_quantity').attr('placeholder','Quantity');
    var buttons = $('form#prepare button');
    buttons.click(function(){
        $('form#prepare select#id_unit').val($(this).attr('data-value'));
        buttons.attr('data-bs-toggle','').attr('aria-pressed','').removeClass('active');
        $(this).attr('data-bs-toggle','button').attr('aria-pressed','true').addClass('active');
    });
    /* recipe table */
    $('.recipe-table-checkbox').click(function(){
        if($(this).prop('checked')){
            $(this).parent().parent().addClass('text-decoration-line-through');
        }
        else{
            $(this).parent().parent().removeClass('text-decoration-line-through');
        }
    });
});