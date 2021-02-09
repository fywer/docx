'use strict'
import handler from "../util/handler.js";

const saveFile = (event) => {
    event.preventDefault();
    const btoncargarfile = document.getElementById("bton_cargarfile");
    const files= btoncargarfile.files;
    try {
        if (files.length == 0) {
            window.alert("No ha seleccionado un archivo.");
            throw "No ha seleccionado un archivo.";
        }
    } catch (e) {
        console.warn(e);
        return;
    }
    files[0].arrayBuffer().
    then( buffer => {
        const blob = new Blob([new Uint8Array(buffer)], {type : 'application/pdf'});
        const lector = new FileReader();
        lector.onload = (event) => {
            let pdf64 = window.btoa(lector.result);
            let documento = {
                "nombre" : files[0].name,
                "tipo" : files[0].type,
                "tamanio" : files[0].size,
                "contenido" : pdf64
            }
            setFile(documento);
        }
        lector.readAsBinaryString(blob);
    }).
    catch(handler.error);        
}
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
        window.alert(data.msg);
        document.getElementById("bton_cargarfile").value = '';
    }).
    catch(handler.error);
}
window.addEventListener('load', (event) => {
    const formagregarfile = document.getElementById("form_agregarfile");
    formagregarfile.addEventListener('submit', saveFile);
});
