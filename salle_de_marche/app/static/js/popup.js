$(document).ready(function(){

    //-------------------------- cours ---------------------------//

    $("#openCoursModal").click(function(){
        $("#addCours").modal('show');
    });

    $("#openModifierCoursModal").click(function(){ // Correction ici
        $("#editCours").modal('show');
    });


    //-------------------------- bande ---------------------------//

    $("#openBandeModal").click(function(){
        $("#addBande").modal('show');
    });

    //-------------------------- importation ---------------------------//

    $("#openImportModal").click(function(){
        $("#import").modal('show');
    });

    $("#openVisualisationtModal").click(function(){
        $("#visualisation").modal('show');
    });

    //  annuler
    $("#addCours #annuler").click(function(){
        $("#addCours").modal('hide');
    });

    $("#addBande #annuler").click(function(){
        $("#addBande").modal('hide');
    });

    $("#import #annuler").click(function(){
        $("#import").modal('hide');
    });

    $("#addBandeForm").submit(function(event) {
        // Validation du formulaire
        var max = $("#bandeMax").val();
        var min = $("#bandeMin").val();

        if (min >= max) {
            $("#minError").text("La valeur minimale doit être inférieure à la valeur maximale.");
            event.preventDefault();
        } else {
            $("#minError").text("");
        }
    });
});
