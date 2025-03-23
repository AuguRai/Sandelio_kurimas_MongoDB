Šis web servisas naudoja MongoDB duomenų bazę ir leidžia atlikti įvairias operacijas su sandėliais ir produktais. 
Pagrindinė funkcionalumo dalis apima produktų registravimą, sandėlių valdymą ir inventoriaus sekimą.
Programoje galima vykdyti šiuos veiksmus: pridėti, 
gauti informaciją apie produktus ir sandėlius, pašalinti produktus ar sandėlius, taip pat sekti sandėlių inventorių ir jų vertę.

## Programos paleidimas

Vienas iš būdų paleisti programą naudojant **Docker Desktop**:

* Atsisiųskite ir susidiekite Docker Desktop
* Pasileiskite Docker konteinerį: docker run -p 27017:27017 -d mongo

Programos veikimui testuoti galima naudoti Postman.

## **Operacijos produktams**
/products (PUT) - leidžia registruoti produktą, suteikiant produktui pavadinimą, kategoriją ir kainą. Jeigu trūksta kokios nors informacijos arba kaina nėra teisinga, bus grąžinamas klaidos pranešimas.

/products (GET) - leidžia gauti visus produktus arba tik tam tikros kategorijos produktus. Jeigu nurodyta kategorija, bus grąžinti tik tos kategorijos produktai.

/products/<productId> (GET) - leidžia gauti informaciją apie konkretų produktą pagal jo ID.

/products/<productId> (DELETE) - leidžia ištrinti produktą pagal jo ID.

## **Operacijos sandėliams**
/warehouses (PUT) - leidžia registruoti sandėlį suteikiant jam pavadinimą, vietą ir talpą.

/warehouses/<warehouseId> (GET) - leidžia gauti informaciją apie konkretų sandėlį pagal jo ID.

/warehouses/<warehouseId> (DELETE) - leidžia ištrinti sandėlį pagal jo ID.

## **Operacijos sandėlio inventoriui**

/warehouses/<warehouseId>/inventory (PUT) - leidžia pridėti produktą į sandėlio inventorių, nurodant produkto ID ir kiekį.

/warehouses/<warehouseId>/inventory (GET) - leidžia gauti visą sandėlio inventorių (visus produktus ir jų kiekius).

/warehouses/<warehouseId>/inventory/<inventoryId> (GET) - leidžia gauti konkretų inventoriaus elementą pagal produkto ID.

/warehouses/<warehouseId>/inventory/<inventoryId> (DELETE) - leidžia ištrinti konkretų inventoriaus elementą pagal produkto ID.

## **Operacijos sandėlio statistikoms**

/warehouses/<warehouseId>/value (GET) - leidžia gauti sandėlio vertę, kuri apskaičiuojama atsižvelgiant į produktų kiekį ir kainas sandėlio inventoriuje.

/statistics/warehouse/capacity (GET) - leidžia gauti visų sandėlių talpą, užimtą vietą ir laisvą vietą apskaičiuojant pagal sandėlio talpą ir inventorių.

/statistics/products/by/category (GET) - leidžia gauti produktų skaičių pagal kategorijas.

## **Papildomos operacijos**
/cleanup (POST) - leidžia išvalyti visus duomenis iš produktų ir sandėlių kolekcijų.


