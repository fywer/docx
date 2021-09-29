'use strict'
import handler from "../util/handler.js";

const setFile = (documento) => {
    const uri = '/file';
    const request = {
        method : 'POST',
        body : JSON.stringify(documento),
        headers : {
            'Content-Type' : 'application/json; charset=utf-8'
        }
    }
    fetch(uri, request).
    then(handler.responseJSON).
    then( data => {
        document.getElementById("bton_cargarfile").value = '';
        const btonuploadfile = document.querySelector("input[form='form_agregarfile']")
        btonuploadfile.disabled = false;
        btonuploadfile.value = "Upload"
        window.alert(data.msg);

    }).
    catch(handler.error);
}
const saveFile = (file) => {
    file.arrayBuffer().
    then( buffer => {
        const blob = new Blob([new Uint8Array(buffer)], {type : 'application/pdf'});
        const lector = new FileReader();
        lector.onload = (event) => {
            let pdf64 = window.btoa(lector.result);
            let documento = {
                "nombre" : file.name,
                "tipo" : file.type,
                "tamanio" : file.size,
                "contenido" : pdf64
            }
            let formagregarfile = document.querySelectorAll("#form_agregarfile"); 
            formagregarfile.forEach( item => {
                item.disabled = true 
            });
            setFile(documento);
        }
        lector.readAsBinaryString(blob);
    }).
    catch(handler.error);        
}
window.addEventListener('load', (event) => {
    const formagregarfile = document.getElementById("form_agregarfile");
    formagregarfile.addEventListener('submit', (event) => {
        event.preventDefault();
        const btonuploadfile = document.querySelector("input[form='form_agregarfile']");
        btonuploadfile.disabled = true;
        btonuploadfile.value = "Loading...";
        const btoncargarfile = document.getElementById("bton_cargarfile");
        const files= btoncargarfile.files;
        try {
            if (files.length == 0) {
                window.alert("No ha seleccionado un archivo.");
                throw "No ha seleccionado un archivo.";
            }
        } 
        catch (e) {
            console.warn(e);
            btonuploadfile.disabled = false;
            btonuploadfile.value = "Upload";
            return;
        }
        saveFile(files[0]);
    });
});