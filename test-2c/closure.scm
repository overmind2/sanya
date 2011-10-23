(define (cons a b)
  (lambda (f)
    (f a b)))

(define (car c)
  (c (lambda (a b)
       a)))

(define (cdr c)
  (c (lambda (a b)
       b)))

(define (fibo n)
  (if (< n 2) n
    (+ (fibo (+ n -1))
       (fibo (+ n -2)))))

(display (car (cons 1 2)))
(newline)

(display (fibo 38))
(newline)

