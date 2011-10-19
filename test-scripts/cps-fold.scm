
(define cfold1
  (lambda (proc/k result args)
    (if (null? args) result
        (proc/k (car args)
                result
                (lambda (result)
                  (cfold1 proc/k result (cdr args)))))))

(define proc->proc/k
  (lambda (proc)
    (lambda (a b cont)
      (proc a (cont b)))))

(define proc->rproc/k
  (lambda (proc)
    (lambda (a b cont)
      (cont (proc a b)))))

(define cfold
  (lambda (proc init args)
    (cfold1 (proc->proc/k proc)
            init
            args)))

(define rcfold
  (lambda (proc init args)
    (cfold1 (proc->rproc/k proc)
            init
            args)))

(define cmap1
  (lambda (proc/k result args)
    (if (null? args) result
        (proc/k (car args)
                (lambda (presult)
                  (cmap1 proc/k (cons presult result) (cdr args)))))))

(display (cmap1 (lambda (x k) (k (+ x 1)))
                '()
                '(1 2 3)))

