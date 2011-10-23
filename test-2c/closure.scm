(define (caar x) (car (car x)))
(define (cadr x) (car (cdr x)))
(define (cddr x) (cdr (cdr x)))
(define (caaar x) (car (car (car x))))
(define (caadr x) (car (car (cdr x))))
(define (caddr x) (car (cdr (cdr x))))
(define (cdddr x) (cdr (cdr (cdr x))))

; lol!
(define (apply proc args)
  (define len (length args))
  (if (= len 0) (proc)
  (if (= len 1) (proc (car args))
  (if (= len 2) (proc (car args) (cadr args))
  (if (= len 3) (proc (car args) (cadr args) (caddr args))
  (if (= len 4) (proc (car args) (cadr args) (caddr args) (car (cdddr args)))))))))

(define (print x)
  (display x)
  (newline))

(define (fibo n)
  (if (< n 2) n
    (+ (fibo (- n 1))
       (fibo (- n 2)))))

;; TCO
(define (sum n)
  (define (sum1 n accu)
    (if (< n 1) accu
      (begin
        (sum1 (- n 1) (+ n accu)))))
  (sum1 n 0))

;; in terms of memory allocation, csc is much better!
;; tco
(define (range n)
  (define (range1 n result)
    (if (< n 0) result
      (range1 (- n 1) (cons (- n 1) result))))
  (range1 n '()))

; tco
(define (length lis)
  (define (length1 lis result)
    (if (null? lis) result
      (length1 (cdr lis) (+ result 1))))
  (length1 lis 0))

; tco
(define (reverse lis)
  (define (reverse1 lis result)
    (if (null? lis) result
      (reverse1 (cdr lis) (cons (car lis) result))))
  (reverse1 lis '()))

; tco
(define (map proc args)
  (define (map1 proc args result)
    (if (null? args) result
      (map1 proc (cdr args) (cons (proc (car args)) result))))
  (reverse (map1 proc args '())))

(define (for-each proc args)
  (if (null? args) #f
    (begin
      (proc (car args))
      (for-each proc (cdr args)))))

(define (append lis1 lis2)
  (define (append1 rev-lis lis)
    (if (null? lis) rev-lis
      (append1 (cons (car lis) rev-lis) (cdr lis))))

  (define rev-lis1 (reverse lis1))
  (reverse (append1 rev-lis1 lis2)))

(define (main)
  (define l1 '(1 2 3))
  (define l2 '(3 2 1))
  (print (append l1 l2)))

(main)

