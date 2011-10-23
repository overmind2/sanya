(define (make-counter)
  (define c 1)
  (lambda ()
    (set! c (+ c 1))
    c))

(define (fibo n)
  (if (< n 2) n
    (+ (fibo (+ n -1))
       (fibo (+ n -2)))))

(define (print x)
  (display x)
  (newline))

(define (main)
  (print (fibo 30)))

(main)
