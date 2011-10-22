
(define (loop n)
  (if (< n 1) n
    (loop (- n 1))))

(define (list . x)
  x)

(define (make-counter)
  (define c 1)
  (lambda ()
    (set! c (+ c 1))
    c))

(define (main)
  (define c (make-counter))
  (display (c)))
