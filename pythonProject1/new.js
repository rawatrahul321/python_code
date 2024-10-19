function fibo(length){
  const arr = [0,1]
  for (i=2;i<=length;i++){
    arr.push(arr[i-1]+arr[i-2])
  }
  return arr
}
const series = fibo(7)
console.log(series)

let arr = [1,2,3,3,2,1] 
let f = arr.filter((ele,index)=>{
  return arr.indexOf(ele)===index
})
console.log(f)

p2 = 0
p1 =1 
l = []
for (i=0;i<=10;i++){
  cur = p2+p1
  p2 = p1
  p1 = cur
  l.push(p1)

}
console.log(...l)

const user = {
  'id':23,
  'name':'rahul',
  'desc':'SE',
  foo: function (){
    console.log(this.name)
  }
}
Object.defineProperties(user,{'name':{writable:false}})
user.name = "eee"
console.log(user.name)

function foo(){
  console.log(this.name)
  const bar=()=>{
    console.log(this.name)
  }
  bar()
}
foo.call({name:'rahul'})

let arr = [1,2,3,4,5,6]
let arr1 = [22,33]
let d = arr.filter(val=>(val<5)).map(val=>(val*2))
console.log(d)

const person = {
    'name':"rahul",
    'age':23
  }
  Object.keys(person).forEach(value=>{
    console.log(value)
  })

function prime_number(number){
    for (i=2;i<=number/2;i++){
      if (number%i==0){
        return false
      }
      return true
    }
  }
  console.log(prime_number(9))

// function removeduplicate(arr){
//     let unique  = []
//     for (i=0;i<arr.length;i++){
//         if (unique.indexOf(arr[i])===-1){
//             unique.push(arr[i])
//         }
//     }
//     return unique
// }
// console.log(removeduplicate([12,3,4,3,4,5,1,1]))

// string = "I Love Javascript"
// a = string.split(" ")
// function Longest(string){
//   char = a[0]
//   for (i=0;i<a.length;i++){
//     if (a[i].length>char.length){
//         char = a[i]
//     }
//   }
//   return char
// }
// console.log(Longest(string))
// curring

// function add(a){
//     return function(b){
//       return function(c){
//         return a+b+c
//       }
//     }
//   }
//   a = add(10)
//   b = a(2)
//   c = b(3)
//   console.log(c)
//   console.log(add(10)(2)(3))

//   const calc =(a)=>(b)=>(c)=>a+b+c;
//   console.log(calc(10)(4)(5))

  // High ROrder Fucntion and Call Back 

//   function add(a,b,cb){
//     let result =a +b
//     cb(result)
//   }
//   function showresult(val){
//     console.log(val)
//   }
//   add(2,3,showresult)

//   function rever(str){
//     return str.split("").reverse().join("")
//   }
//   console.log(rever("rahul"))

