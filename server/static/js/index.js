angular.module("DocumentoService", []).
    factory ("mostrarModal", function () 
    {
        var interfaz =
        {
            main : function (mensaje)
            {
                this.mensaje = mensaje
            },
            setup : function ()
            {
                return { 
                    buttons:[{text: "cool!", key:27/*Esc*/}],
                    focus: { element:0 }
                };
            },
            prepare : function() {
                this.setContent(this.message);
            }
        }
        return interfaz;
    })
    .controller ("Documentos", function ($scope, $http, $window) 
    {
        angular.element($window).on('load', function () {})
		$scope.fetchData = (urlapi, request) => {
            return new Promise( (resolve, reject) =>
            {
                fetch(urlapi, request).
                then( response => 
                {
                    if ( response.status >= 200 && response.status <= 299 )
                    {
                        resolve(response.json());
                    }
                    else
                    {
                        console.error(response);
                        reject(response.json());
                    }
                })
            })
        };
		$scope.setFile = (documento) => 
        {
            return new Promise( (resolve, reject) => 
            {
                const request =
                    
                    {
                        method : 'POST',
                        body : JSON.stringify({'comprobante':documento}),
                        headers :
                        {
                            'Content-Type' : 'application/json; charset=utf-8'
                        }
                    }   
				const uri = '/file';
                $scope.fetchData(`${uri}`, request).
                then( response => 
                {
                    resolve(response);
                }).
                catch(e =>
                {
                    reject(e);
                });
            });
        }
		 
		$scope.uploadFile = () =>
		{
			btonuploadfile = document.querySelector("input[form='form_agregarfile']");
            btonuploadfile.disabled = true;
            btonuploadfile.value = "Loading...";
            btoncargarfile = document.getElementById("bton_cargarfile");
            files= btoncargarfile.files;
			
			try 
            {
                if (files.length == 0) 
                {
                    window.alert("No ha seleccionado un archivo.");
                    throw "No ha seleccionado un archivo.";
                }
                else
                {
                    console.warn(files[0]);
                    $scope.saveFile(files[0]).
                    then( response =>
                    {
                        //$scope.$apply = function () 
                        //{
                            $scope.documentos.push(response)
                        //}
                        console.log(response)
                        alertify.success("Se ha almacenado:: "+response["nombre"])
                        document.getElementById("bton_cargarfile").value = '';
                        const btonuploadfile = document.querySelector("input[form='form_agregarfile']")
                        $scope.descargarXML(response["cfdi"], response["nombre"] )
                        btonuploadfile.disabled = false;
                        btonuploadfile.value = "Upload"
                    }).
                    catch( error =>
                    {
                        error.then(error => 
                        {
                            alertify.warning('Por favor, intentalo mas tarde. Código: ' + error['error'])
                            btonuploadfile.disabled = false;
                            btonuploadfile.value = "Upload"
                        })
                    });
                }
            } 
            catch (e)
            {
                console.warn(e);
                btonuploadfile.disabled = false;
                btonuploadfile.value = "Upload";
                return;
            }
		}	
		
		$scope.saveFile = (file) => 
		{
            return new Promise( (resolve, reject) => 
            {
                file.arrayBuffer().
                then( buffer => {
                    const blob = new Blob([new Uint8Array(buffer)], {type : file["type"]});
                    const reader  = new FileReader();
                    reader.onload = (event) =>
                    {
                        let xml64 = window.btoa(reader.result);
                        let tipo = file["type"].split('/')[1]
                        let type = 0;
                        switch (tipo)
                        {
                            case 'xml':
                                type = 1;
                                break;
                            default:
                                type = 0;
                        }
                        if (type === 0)
                        {
                            reject("El fomato no es válido.");
                        }
                        else
                        { 
                            let decodeData = window.atob(xml64);
                            let buffer = new ArrayBuffer(xml64.length);
                            let view = new Uint8Array(buffer);
                            for (let i = 0; i < xml64.length; i ++) {
                                view[i] = decodeData.charCodeAt(i);
                            }
                            let file = NaN;
                            console.log(type);
                            switch (type) 
                            {
                                case 1:
                                    file = new Blob([view], {type: 'text/xml'});
                                    ruta = URL.createObjectURL(file);
                                    break;
                                default:
                                    ruta = "#"
                                    break;
                            }
                            console.log(file)
                            let formagregarfile = document.querySelectorAll("#form_agregarfile"); 
                            formagregarfile.forEach( item => 
                            {
                                item.disabled = true 
                            });
							
                            $scope.setFile(xml64).
                            then( mensaje =>
                            {
                                resolve(mensaje);
                            }).
                            catch( error => 
                            {
                                reject(error)

                            });
                        }   
                    }
                    reader.readAsBinaryString(blob);
                }).
                catch(e => 
                {
                    console.error(e);
                    window.alert('Por favor, intentalo mas tarde. Código: ' + e);
                });
            });
        }
		
		$scope.showUpload = function ()
        {   
            const sect_upload = document.getElementById("sect_upload")
            if (!sect_upload.hasAttribute("hidden"))
            {
                sect_upload.setAttribute("hidden", "hidden")
            } 
            else
            {
                sect_upload.removeAttribute("hidden")
            }
        }
		
        $scope.$watch('documentos', function(newVal, oldVal) {
        
            if (newVal !== oldVal) {
              // Aquí puedes realizar acciones cuando la lista $scope.documentos cambie
              console.log('La lista documentos ha cambiado:', newVal);
            }
        }, true);
        
        $scope.base64ToBytes = function(base64)
        {
            const binString = atob(base64);
            return Uint8Array.from(binString, (m) => m.codePointAt(0));
        }
        $scope.bytesToBase64 = function (bytes)
        {
            const binString = String.fromCodePoint(...bytes);
            return btoa(binString);
          }
        $scope.descargarXML = function (xmlcomprobante, nombreArchivo)
        {
            // xmlbin = $scope.base64ToBytes(xmlcomprobante)
            // xmlb64 = $scope.bytesToBase64(xmlbin)
            var archivoBlob = new Blob([decodeURIComponent(escape(atob(xmlcomprobante)))], {type: 'text/xml'});
            var urlArchivoXML = $window.URL.createObjectURL(archivoBlob);
            var enlaceDescarga = document.createElement('a');
            enlaceDescarga.href = urlArchivoXML;
            enlaceDescarga.download = nombreArchivo;
            enlaceDescarga.click();
            $window.URL.revokeObjectURL(urlArchivoXML)
        }

        $scope.mostrarDialogo = function (id) 
        {
            if (id == undefined)
            {
                console.error('El id no ha sido definido.')
            }
            else
            {
                if(!alertify.myAlert) 
                { 
                    //define a new dialog
                    alertify.dialog('myAlert',function ()
                    {
                        return {
                            main : function( doc ) {                               
                                this.doc = doc                            
                        },
                        setup : function() {
                            return { 
                                buttons:[
                                {
                                    text: "Salir", 
                                    key:27/*Esc*/
                                
                                }],
                                focus: { element:0 }
                            };
                        },
                        prepare : function () {
                            console.log(this.doc)
                            contenido = `
                                <h6>Hash ID</h6>
                                <p> ${this.doc['nombre']} </p> 
                                <h6>Resumen</h6>
                                <p> ${this.doc['fecha']} </p>
                                <button ng-click=${$scope.descargarXML( atob(this.doc['contenido']), this.doc['nombre']  )} > Descargar </button>
                            `
                            this.setContent(contenido);
                        }
                    }});
                }
                const request =
                {
                    method : 'GET',
                    headers :
                    {
                        'Content-Type' : 'application/json; charset=utf-8'
                    }
                }
                const uri = '/file/';
                const data = $scope.fetchData(`${uri}${id}`, request);
                data.
                then( response => 
                {
                    var documento = response;
                    alertify.myAlert(documento);
                }).
                catch(e =>
                {
                    console.error(e);
                    window.alert('Por favor, intentalo mas tarde. Código: ' + e);
                });                   
            }  
        }
        
        $scope.documentos = []
        $http.get("/file").then
        ( 
            function (response) 
            {
                console.log(response);
                if (response.data.length > 0) 
                {
                    $scope.documentos = response.data;
                } 
                else
                {
                    alertify.warning("No se han encontrado documentos.");   
                }            
            },
            function (error) 
            {
                alertify.error(error.data.msg);  
                console.log(error) 
            }
        )
    }
);