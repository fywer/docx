class Documento {
    constructor(id, nombre, tipo, tamanio, ruta) {
        this.id = id;
        this.nombre = nombre;
        this.tipo = tipo;
        this.tamanio = tamanio;
        this.ruta = ruta;
    }
    parser(data) {
        this.id = data.id;
        this.nombre = data.nombre;
        this.tipo = data.tipo;
        this.tamanio = data.tamanio;
        this.ruta = data.ruta;
        return this;
    }
    get getId() {
        return this.id;
    }
    get getTipo() {
        return this.tipo;
    }
    get getNombre() {
        return this.nombre;
    }
    get getTamanio() {
        return this.tamanio;
    }
    get getRuta() {
        return this.ruta;
    }
    set setId(id) {
        this.id = id;
    }
    set setNombre(nombre) {
        this.nombre = nombre;
    }
    set setTipo(tipo) {
        this.tipo = tipo;
    }
    set setTamanio(tamanio) {
        this.tamanio = tamanio;
    }
    set setRuta(ruta) {
        this.ruta = ruta;
    }
}
export { Documento }